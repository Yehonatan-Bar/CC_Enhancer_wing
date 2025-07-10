#!/usr/bin/env python3
"""
Example Usage of the Dual-Tag Logging System

This script demonstrates how to integrate and use the logging system
in a real application scenario.
"""

import time
import random
from logger import (
    DualTagLogger, LogLevel, LogFilter, 
    configure_logger, get_logger,
    ConsoleLogHandler, FileLogHandler
)
from log_analyzer import LogAnalyzer, LogViewer, LogSortKey


# Feature tags - User-facing functionality
class Features:
    USER_AUTH = "user_authentication"
    DATA_PROCESSING = "data_processing"
    FILE_OPERATIONS = "file_operations"
    API_CALLS = "api_calls"
    REPORT_GENERATION = "report_generation"


# Module tags - Internal system modules
class Modules:
    AUTH_MODULE = "auth_module"
    DATABASE = "database"
    FILE_HANDLER = "file_handler"
    API_CLIENT = "api_client"
    ANALYTICS = "analytics"
    UTILS = "utils"


class UserAuthenticationService:
    """Example service demonstrating logging"""
    
    def __init__(self, logger: DualTagLogger):
        self.logger = logger
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate a user"""
        self.logger.info(
            Features.USER_AUTH,
            Modules.AUTH_MODULE,
            "authenticate_user",
            "Starting user authentication",
            username=username,
            ip_address="192.168.1.100"
        )
        
        # Simulate authentication process
        time.sleep(0.1)
        
        # Simulate checking credentials
        if username == "admin" and password == "password":
            self.logger.info(
                Features.USER_AUTH,
                Modules.AUTH_MODULE,
                "authenticate_user",
                "User authenticated successfully",
                username=username,
                duration=0.1
            )
            return True
        else:
            self.logger.warning(
                Features.USER_AUTH,
                Modules.AUTH_MODULE,
                "authenticate_user",
                "Authentication failed",
                username=username,
                reason="Invalid credentials"
            )
            return False
    
    def check_permissions(self, username: str, resource: str) -> bool:
        """Check user permissions"""
        self.logger.debug(
            Features.USER_AUTH,
            Modules.DATABASE,
            "check_permissions",
            "Checking user permissions",
            username=username,
            resource=resource
        )
        
        # Simulate permission check
        has_permission = random.choice([True, False])
        
        if has_permission:
            self.logger.info(
                Features.USER_AUTH,
                Modules.DATABASE,
                "check_permissions",
                "Permission granted",
                username=username,
                resource=resource
            )
        else:
            self.logger.warning(
                Features.USER_AUTH,
                Modules.DATABASE,
                "check_permissions",
                "Permission denied",
                username=username,
                resource=resource
            )
        
        return has_permission


class DataProcessor:
    """Example data processing service"""
    
    def __init__(self, logger: DualTagLogger):
        self.logger = logger
    
    def process_data(self, data_id: str, data_size: int) -> dict:
        """Process some data"""
        start_time = time.time()
        
        self.logger.info(
            Features.DATA_PROCESSING,
            Modules.ANALYTICS,
            "process_data",
            "Starting data processing",
            data_id=data_id,
            data_size=data_size
        )
        
        try:
            # Simulate data processing
            time.sleep(random.uniform(0.1, 0.5))
            
            # Simulate occasional errors
            if random.random() < 0.2:
                raise ValueError("Data validation failed")
            
            result = {
                "processed_records": data_size,
                "status": "success"
            }
            
            elapsed_time = time.time() - start_time
            
            self.logger.info(
                Features.DATA_PROCESSING,
                Modules.ANALYTICS,
                "process_data",
                "Data processing completed",
                data_id=data_id,
                elapsed_time=elapsed_time,
                result=result
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                Features.DATA_PROCESSING,
                Modules.ANALYTICS,
                "process_data",
                f"Data processing failed: {str(e)}",
                data_id=data_id,
                error_type=type(e).__name__,
                elapsed_time=time.time() - start_time
            )
            raise


class FileManager:
    """Example file operations service"""
    
    def __init__(self, logger: DualTagLogger):
        self.logger = logger
    
    def save_file(self, filename: str, content: str) -> bool:
        """Save a file"""
        self.logger.info(
            Features.FILE_OPERATIONS,
            Modules.FILE_HANDLER,
            "save_file",
            "Attempting to save file",
            filename=filename,
            content_size=len(content)
        )
        
        try:
            # Simulate file operations
            time.sleep(0.05)
            
            self.logger.info(
                Features.FILE_OPERATIONS,
                Modules.FILE_HANDLER,
                "save_file",
                "File saved successfully",
                filename=filename,
                bytes_written=len(content)
            )
            return True
            
        except Exception as e:
            self.logger.error(
                Features.FILE_OPERATIONS,
                Modules.FILE_HANDLER,
                "save_file",
                f"Failed to save file: {str(e)}",
                filename=filename,
                error_type=type(e).__name__
            )
            return False


class APIClient:
    """Example API client"""
    
    def __init__(self, logger: DualTagLogger):
        self.logger = logger
    
    def make_request(self, endpoint: str, method: str = "GET") -> dict:
        """Make an API request"""
        request_id = f"req_{random.randint(1000, 9999)}"
        
        self.logger.info(
            Features.API_CALLS,
            Modules.API_CLIENT,
            "make_request",
            "Making API request",
            request_id=request_id,
            endpoint=endpoint,
            method=method
        )
        
        # Simulate API call
        start_time = time.time()
        time.sleep(random.uniform(0.1, 0.3))
        
        # Simulate responses
        status_code = random.choice([200, 200, 200, 404, 500])
        response_time = time.time() - start_time
        
        if status_code == 200:
            self.logger.info(
                Features.API_CALLS,
                Modules.API_CLIENT,
                "make_request",
                "API request successful",
                request_id=request_id,
                status_code=status_code,
                response_time=response_time
            )
            return {"status": "success", "data": {"id": 123}}
        else:
            self.logger.error(
                Features.API_CALLS,
                Modules.API_CLIENT,
                "make_request",
                "API request failed",
                request_id=request_id,
                status_code=status_code,
                response_time=response_time
            )
            return {"status": "error", "code": status_code}


def generate_report(logger: DualTagLogger, data: dict) -> None:
    """Generate a report using multiple modules"""
    report_id = f"report_{random.randint(10000, 99999)}"
    
    logger.info(
        Features.REPORT_GENERATION,
        Modules.ANALYTICS,
        "generate_report",
        "Starting report generation",
        report_id=report_id
    )
    
    # Simulate fetching data from database
    logger.debug(
        Features.REPORT_GENERATION,
        Modules.DATABASE,
        "generate_report",
        "Fetching data from database",
        report_id=report_id,
        query="SELECT * FROM metrics"
    )
    
    # Simulate processing
    time.sleep(0.2)
    
    # Simulate file generation
    logger.info(
        Features.REPORT_GENERATION,
        Modules.FILE_HANDLER,
        "generate_report",
        "Writing report to file",
        report_id=report_id,
        filename=f"{report_id}.pdf"
    )
    
    logger.info(
        Features.REPORT_GENERATION,
        Modules.ANALYTICS,
        "generate_report",
        "Report generation completed",
        report_id=report_id,
        duration=0.3
    )


def demonstrate_logging_system():
    """Main demonstration function"""
    
    # Configure the logger
    logger = configure_logger(
        name="DemoApp",
        console=True,
        file_path="demo_app.log",
        min_level=LogLevel.DEBUG
    )
    
    print("=== Dual-Tag Logging System Demonstration ===\n")
    
    # Initialize services
    auth_service = UserAuthenticationService(logger)
    data_processor = DataProcessor(logger)
    file_manager = FileManager(logger)
    api_client = APIClient(logger)
    
    # Simulate application flow
    print("\n1. User Authentication Flow:")
    auth_service.authenticate_user("admin", "password")
    auth_service.authenticate_user("user", "wrongpass")
    auth_service.check_permissions("admin", "/api/users")
    
    print("\n2. Data Processing Flow:")
    for i in range(3):
        try:
            data_processor.process_data(f"dataset_{i}", 1000 * (i + 1))
        except:
            pass
    
    print("\n3. File Operations Flow:")
    file_manager.save_file("output.txt", "Sample content")
    file_manager.save_file("report.pdf", "Report data" * 100)
    
    print("\n4. API Calls Flow:")
    for _ in range(4):
        api_client.make_request("/api/users", "GET")
    
    print("\n5. Report Generation Flow:")
    generate_report(logger, {"metric": "value"})
    
    # Wait for all logs to be processed
    time.sleep(0.5)
    
    # Demonstrate analysis capabilities
    print("\n\n=== Log Analysis Demonstration ===\n")
    
    analyzer = LogAnalyzer(logger)
    viewer = LogViewer(analyzer)
    
    # Get all logs
    all_logs = logger.get_all_logs()
    
    # 1. Feature-based view
    print("\n--- Feature-Based Analysis ---")
    feature_summary = analyzer.get_feature_summary(all_logs)
    for feature, stats in feature_summary.items():
        print(f"\nFeature: {feature}")
        print(f"  Total logs: {stats['count']}")
        print(f"  Modules involved: {', '.join(stats['modules'])}")
        print(f"  Log levels: {stats['levels']}")
    
    # 2. Module-based view
    print("\n\n--- Module-Based Analysis ---")
    module_summary = analyzer.get_module_summary(all_logs)
    for module, stats in module_summary.items():
        print(f"\nModule: {module}")
        print(f"  Total logs: {stats['count']}")
        print(f"  Features using this module: {', '.join(stats['features'])}")
        print(f"  Log levels: {stats['levels']}")
    
    # 3. Error analysis
    print("\n\n--- Error Analysis ---")
    error_analysis = analyzer.get_error_analysis(all_logs)
    print(f"Total errors: {error_analysis['error_count']}")
    print(f"Total warnings: {error_analysis['warning_count']}")
    if error_analysis['errors_by_feature']:
        print("\nErrors by feature:")
        for feature, count in error_analysis['errors_by_feature'].items():
            print(f"  {feature}: {count}")
    
    # 4. Performance metrics
    print("\n\n--- Performance Analysis ---")
    perf_metrics = analyzer.get_performance_metrics(all_logs)
    if "avg_duration" in perf_metrics:
        print(f"Average operation duration: {perf_metrics['avg_duration']:.3f}s")
        print(f"Slowest operation: {perf_metrics['max_duration']:.3f}s")
        print("\nPerformance by function:")
        for func, stats in perf_metrics['by_function'].items():
            print(f"  {func}: avg={stats['avg']:.3f}s, count={stats['count']}")
    
    # 5. Filtered views
    print("\n\n--- Filtered Log Examples ---")
    
    # Filter by feature
    auth_logs = logger.get_logs_by_feature(Features.USER_AUTH)
    print(f"\nAuthentication logs ({len(auth_logs)} entries):")
    for log in auth_logs[:3]:
        print(f"  {log.to_formatted_string()}")
    
    # Filter by module
    db_logs = logger.get_logs_by_module(Modules.DATABASE)
    print(f"\nDatabase module logs ({len(db_logs)} entries):")
    for log in db_logs[:3]:
        print(f"  {log.to_formatted_string()}")
    
    # Custom filter
    error_filter = LogFilter(levels=[LogLevel.ERROR, LogLevel.CRITICAL])
    error_logs = logger.get_filtered_logs(error_filter)
    print(f"\nError logs ({len(error_logs)} entries):")
    for log in error_logs[:3]:
        print(f"  {log.to_formatted_string()}")
    
    # 6. Export capabilities
    print("\n\n--- Exporting Logs ---")
    
    # Export all logs to JSON
    logger.export_logs("all_logs.json", format_type="json")
    print("Exported all logs to all_logs.json")
    
    # Export errors to CSV
    logger.export_logs("errors.csv", log_filter=error_filter, format_type="csv")
    print("Exported error logs to errors.csv")
    
    # Generate full report
    report = analyzer.generate_report(all_logs)
    with open("analysis_report.json", "w") as f:
        import json
        json.dump(report, f, indent=2)
    print("Generated comprehensive analysis report: analysis_report.json")
    
    print("\n\n=== Demonstration Complete ===")


if __name__ == "__main__":
    demonstrate_logging_system()