#!/usr/bin/env python3
"""
Fetch URL content script - Gets a URL from user and returns its content.
Handles various content types and provides robust error handling.
"""

import sys
import argparse
import requests
import logging
import socket
import ipaddress
from datetime import datetime
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def is_private_ip(hostname):
    """
    Check if hostname resolves to private/internal IP address.
    
    Args:
        hostname (str): Hostname to check
        
    Returns:
        bool: True if private/internal IP, False otherwise
    """
    try:
        # Resolve hostname to IP
        ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip)
        
        # Check if private, reserved, loopback, or link-local
        return (
            ip_obj.is_private or 
            ip_obj.is_reserved or 
            ip_obj.is_loopback or
            ip_obj.is_link_local or
            str(ip).startswith('169.254.')  # AWS metadata service
        )
    except Exception:
        # If resolution fails, consider it unsafe
        return True


def sanitize_url_for_logging(url):
    """
    Remove sensitive information from URL for safe logging.
    
    Args:
        url (str): URL to sanitize
        
    Returns:
        str: Sanitized URL
    """
    try:
        parsed = urlparse(url)
        # Remove query parameters and fragment
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    except:
        return "[invalid-url]"


def validate_url(url):
    """
    Validate if the provided string is a valid and safe URL.
    
    Args:
        url (str): URL string to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL cannot be empty"
    
    try:
        result = urlparse(url)
        
        # Check scheme
        if result.scheme not in ['http', 'https']:
            return False, "Only HTTP(S) URLs are allowed"
        
        # Check for netloc
        if not result.netloc:
            return False, "Invalid URL format"
        
        # Check URL length
        if len(url) > 2048:
            return False, "URL too long (max 2048 characters)"
        
        # Extract hostname for SSRF check
        hostname = result.hostname
        if not hostname:
            return False, "Invalid hostname"
        
        # Check for private IPs (SSRF protection)
        if is_private_ip(hostname):
            return False, "Access to private/internal addresses is not allowed"
        
        # Check for common metadata endpoints
        blocked_hosts = [
            'metadata.google.internal',
            'metadata.azure.com',
            '169.254.169.254'
        ]
        if hostname.lower() in blocked_hosts:
            return False, "Access to metadata endpoints is not allowed"
        
        return True, None
        
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


# Allowed content types for security
ALLOWED_CONTENT_TYPES = [
    'text/', 'application/json', 'application/xml',
    'application/xhtml+xml', 'application/javascript',
    'application/ld+json', 'application/atom+xml'
]

def is_allowed_content_type(content_type):
    """Check if content type is allowed."""
    if not content_type:
        return False
    ct_lower = content_type.lower()
    return any(allowed in ct_lower for allowed in ALLOWED_CONTENT_TYPES)


def fetch_url_content(url, timeout=30, verify_ssl=True, max_size=10*1024*1024):
    """
    Fetch content from the provided URL.
    
    Args:
        url (str): URL to fetch content from
        timeout (int): Request timeout in seconds
        verify_ssl (bool): Whether to verify SSL certificates
        max_size (int): Maximum response size in bytes (default: 10MB)
        
    Returns:
        tuple: (content, content_type, status_code)
    """
    # Validate timeout
    if timeout <= 0:
        raise ValueError(f"Timeout must be positive, got: {timeout}")
    
    # Security warning for disabled SSL
    if not verify_ssl:
        logger.warning("SSL verification is disabled - connection may be insecure!")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; URLFetcher/1.0)',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/json,application/xml;q=0.9,*/*;q=0.8',
        'DNT': '1',
        'X-Requested-With': 'URLFetcher',
        'Cache-Control': 'no-cache'
    }
    
    try:
        # Create session with connection limits
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=3
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Log sanitized URL
        logger.info(f"Fetching content from: {sanitize_url_for_logging(url)}")
        
        response = session.get(
            url, 
            headers=headers, 
            timeout=timeout,
            verify=verify_ssl,
            allow_redirects=True,
            stream=True  # Stream to check size before loading
        )
        response.raise_for_status()
        
        # Check content length
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) > max_size:
            response.close()
            raise ValueError(f"Response too large: {int(content_length)} bytes (max: {max_size})")
        
        # Read content with size limit
        content_chunks = []
        total_size = 0
        for chunk in response.iter_content(chunk_size=8192, decode_unicode=False):
            total_size += len(chunk)
            if total_size > max_size:
                response.close()
                raise ValueError(f"Response exceeded size limit: {max_size} bytes")
            content_chunks.append(chunk)
        
        content = b''.join(content_chunks)
        content_type = response.headers.get('Content-Type', 'unknown')
        
        # Validate content type for security
        if not is_allowed_content_type(content_type):
            logger.warning(f"Potentially unsafe content type: {content_type}")
        
        logger.info(f"Successfully fetched {len(content)} bytes, Content-Type: {content_type}")
        
        # For text content, decode with error handling
        if any(t in content_type.lower() for t in ['text', 'json', 'xml', 'html', 'javascript']):
            try:
                # Try to detect encoding from Content-Type or use chardet
                encoding = response.encoding or 'utf-8'
                text_content = content.decode(encoding)
                return text_content, content_type, response.status_code
            except UnicodeDecodeError:
                logger.warning(f"Failed to decode content as {encoding}, returning as binary")
                return f"Binary content (failed to decode as text), size: {len(content)} bytes", content_type, response.status_code
        else:
            # For binary content, return indication of content type and size
            return f"Binary content ({content_type}), size: {len(content)} bytes", content_type, response.status_code
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error: Request timed out after {timeout} seconds")
        raise
    except requests.exceptions.TooManyRedirects:
        logger.error("Too many redirects")
        raise
    except requests.exceptions.ProxyError:
        logger.error("Proxy error occurred")
        raise
    except requests.exceptions.SSLError:
        logger.error("SSL certificate verification failed")
        raise
    except requests.exceptions.ConnectionError:
        logger.error("Connection error occurred")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error {e.response.status_code}: {e}")
        raise
    except ValueError as e:
        logger.error(f"Value Error: {e}")
        raise
    except MemoryError:
        logger.error(f"Memory Error: Response too large to process")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}")
        raise


def main():
    """Main function to handle command line interface."""
    parser = argparse.ArgumentParser(
        description='Fetch and display content from a URL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s https://example.com
  %(prog)s https://api.example.com/data --timeout 60
  %(prog)s https://self-signed.example.com --no-verify-ssl
        '''
    )
    
    parser.add_argument(
        'url',
        nargs='?',
        help='URL to fetch content from'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    parser.add_argument(
        '--max-size',
        type=int,
        default=10*1024*1024,
        help='Maximum response size in bytes (default: 10MB)'
    )
    parser.add_argument(
        '--no-verify-ssl',
        action='store_true',
        help='Disable SSL certificate verification'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate timeout
    if args.timeout <= 0:
        print(f"Error: Timeout must be positive, got: {args.timeout}")
        sys.exit(1)
    
    # Validate max_size
    if args.max_size <= 0:
        print(f"Error: Max size must be positive, got: {args.max_size}")
        sys.exit(1)
    
    # If no URL provided as argument, prompt user
    if not args.url:
        try:
            url = input("Enter URL to fetch: ").strip()
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)
        except EOFError:
            print("\nNo input provided")
            sys.exit(1)
    else:
        url = args.url
    
    # Warn about SSL verification if disabled
    if args.no_verify_ssl:
        print("\nWARNING: SSL certificate verification is disabled!")
        print("This makes the connection vulnerable to man-in-the-middle attacks.\n")
    
    # Validate URL
    is_valid, error_msg = validate_url(url)
    if not is_valid:
        print(f"Error: {error_msg}")
        if "private" in error_msg or "metadata" in error_msg:
            print("For security reasons, access to internal/private addresses is blocked.")
        sys.exit(1)
    
    # Fetch content
    try:
        content, content_type, status_code = fetch_url_content(
            url,
            timeout=args.timeout,
            verify_ssl=not args.no_verify_ssl,
            max_size=args.max_size
        )
        
        print(f"\n=== URL Content ===")
        print(f"URL: {url}")
        print(f"Status Code: {status_code}")
        print(f"Content-Type: {content_type}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"{'='*50}\n")
        
        print(content)
        
    except requests.exceptions.SSLError:
        print("\nSSL Error: Failed to verify SSL certificate.")
        print("Use --no-verify-ssl flag if you trust this server (not recommended).")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"\nTimeout Error: Request timed out after {args.timeout} seconds.")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("\nConnection Error: Failed to connect to the server.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\nHTTP Error: Server returned status code {e.response.status_code}")
        sys.exit(1)
    except ValueError as e:
        print(f"\nValue Error: {e}")
        sys.exit(1)
    except Exception:
        print("\nAn unexpected error occurred while fetching the URL.")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()