#!/usr/bin/env python3
"""
Fetch URL content script - Gets a URL from user and returns its content.
Handles various content types and provides robust error handling.
"""

import sys
import argparse
import requests
import logging
from datetime import datetime
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def validate_url(url):
    """
    Validate if the provided string is a valid URL.
    
    Args:
        url (str): URL string to validate
        
    Returns:
        bool: True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def fetch_url_content(url, timeout=30, verify_ssl=True):
    """
    Fetch content from the provided URL.
    
    Args:
        url (str): URL to fetch content from
        timeout (int): Request timeout in seconds
        verify_ssl (bool): Whether to verify SSL certificates
        
    Returns:
        tuple: (content, content_type, status_code)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; URLFetcher/1.0)'
    }
    
    try:
        logger.info(f"Fetching content from: {url}")
        response = requests.get(
            url, 
            headers=headers, 
            timeout=timeout,
            verify=verify_ssl,
            allow_redirects=True
        )
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', 'unknown')
        logger.info(f"Successfully fetched {len(response.content)} bytes, Content-Type: {content_type}")
        
        # For text content, return decoded text
        if 'text' in content_type or 'json' in content_type or 'xml' in content_type:
            return response.text, content_type, response.status_code
        else:
            # For binary content, return indication of content type and size
            return f"Binary content ({content_type}), size: {len(response.content)} bytes", content_type, response.status_code
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout error: Request to {url} timed out after {timeout} seconds")
        raise
    except requests.exceptions.SSLError:
        logger.error(f"SSL Error: SSL certificate verification failed for {url}")
        raise
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection Error: Failed to connect to {url}")
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error {e.response.status_code}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
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
    
    # Validate URL
    if not validate_url(url):
        print(f"Error: '{url}' is not a valid URL")
        print("Please provide a URL starting with http:// or https://")
        sys.exit(1)
    
    # Fetch content
    try:
        content, content_type, status_code = fetch_url_content(
            url,
            timeout=args.timeout,
            verify_ssl=not args.no_verify_ssl
        )
        
        print(f"\n=== URL Content ===")
        print(f"URL: {url}")
        print(f"Status Code: {status_code}")
        print(f"Content-Type: {content_type}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"{'='*50}\n")
        
        print(content)
        
    except Exception as e:
        print(f"\nError fetching URL: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()