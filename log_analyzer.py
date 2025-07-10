#!/usr/bin/env python3
"""
Log Analyzer Module

Provides advanced analysis and sorting capabilities for the dual-tag logging system.
Enables viewing logs from both feature and module perspectives.
"""

from typing import List, Dict, Any, Optional, Callable, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import json
import statistics
from logger import LogEntry, LogLevel, LogFilter, DualTagLogger


class LogSortKey:
    """Defines sorting criteria for logs"""
    
    TIMESTAMP = "timestamp"
    FEATURE_TAG = "feature_tag"
    MODULE_TAG = "module_tag"
    LEVEL = "level"
    FUNCTION_NAME = "function_name"
    
    @staticmethod
    def get_sort_function(key: str, reverse: bool = False) -> Callable[[LogEntry], Any]:
        """Get sorting function for a given key"""
        key_map = {
            LogSortKey.TIMESTAMP: lambda e: e.timestamp,
            LogSortKey.FEATURE_TAG: lambda e: e.feature_tag,
            LogSortKey.MODULE_TAG: lambda e: e.module_tag,
            LogSortKey.LEVEL: lambda e: e.level.value,
            LogSortKey.FUNCTION_NAME: lambda e: e.function_name
        }
        
        if key not in key_map:
            raise ValueError(f"Invalid sort key: {key}")
        
        return key_map[key]


class LogAnalyzer:
    """
    Provides comprehensive analysis capabilities for log entries
    """
    
    def __init__(self, logger: Optional[DualTagLogger] = None):
        self.logger = logger
    
    def sort_logs(self, 
                  logs: List[LogEntry],
                  primary_key: str,
                  secondary_key: Optional[str] = None,
                  reverse: bool = False) -> List[LogEntry]:
        """
        Sort logs by one or two keys
        
        Args:
            logs: List of log entries to sort
            primary_key: Primary sort key
            secondary_key: Optional secondary sort key
            reverse: Sort in descending order
        
        Returns:
            Sorted list of log entries
        """
        if secondary_key:
            # Sort by secondary key first, then primary
            logs = sorted(logs, 
                         key=LogSortKey.get_sort_function(secondary_key),
                         reverse=reverse)
        
        return sorted(logs,
                     key=LogSortKey.get_sort_function(primary_key),
                     reverse=reverse)
    
    def group_by_feature(self, logs: List[LogEntry]) -> Dict[str, List[LogEntry]]:
        """Group logs by feature tag"""
        grouped = defaultdict(list)
        for log in logs:
            grouped[log.feature_tag].append(log)
        return dict(grouped)
    
    def group_by_module(self, logs: List[LogEntry]) -> Dict[str, List[LogEntry]]:
        """Group logs by module tag"""
        grouped = defaultdict(list)
        for log in logs:
            grouped[log.module_tag].append(log)
        return dict(grouped)
    
    def group_by_function(self, logs: List[LogEntry]) -> Dict[str, List[LogEntry]]:
        """Group logs by function name"""
        grouped = defaultdict(list)
        for log in logs:
            grouped[log.function_name].append(log)
        return dict(grouped)
    
    def get_feature_summary(self, logs: List[LogEntry]) -> Dict[str, Dict[str, Any]]:
        """
        Get summary statistics for each feature
        
        Returns dict with:
        - count: Total log entries
        - levels: Count by log level
        - modules: Modules that logged for this feature
        - functions: Functions that logged for this feature
        - time_range: First and last log timestamps
        """
        feature_groups = self.group_by_feature(logs)
        summary = {}
        
        for feature, feature_logs in feature_groups.items():
            level_counts = Counter(log.level.value for log in feature_logs)
            modules = list(set(log.module_tag for log in feature_logs))
            functions = list(set(log.function_name for log in feature_logs))
            timestamps = [log.timestamp for log in feature_logs]
            
            summary[feature] = {
                "count": len(feature_logs),
                "levels": dict(level_counts),
                "modules": modules,
                "functions": functions,
                "time_range": {
                    "start": datetime.fromtimestamp(min(timestamps)).isoformat(),
                    "end": datetime.fromtimestamp(max(timestamps)).isoformat()
                } if timestamps else None
            }
        
        return summary
    
    def get_module_summary(self, logs: List[LogEntry]) -> Dict[str, Dict[str, Any]]:
        """
        Get summary statistics for each module
        
        Returns dict with:
        - count: Total log entries
        - levels: Count by log level
        - features: Features that used this module
        - functions: Functions in this module that logged
        - time_range: First and last log timestamps
        """
        module_groups = self.group_by_module(logs)
        summary = {}
        
        for module, module_logs in module_groups.items():
            level_counts = Counter(log.level.value for log in module_logs)
            features = list(set(log.feature_tag for log in module_logs))
            functions = list(set(log.function_name for log in module_logs))
            timestamps = [log.timestamp for log in module_logs]
            
            summary[module] = {
                "count": len(module_logs),
                "levels": dict(level_counts),
                "features": features,
                "functions": functions,
                "time_range": {
                    "start": datetime.fromtimestamp(min(timestamps)).isoformat(),
                    "end": datetime.fromtimestamp(max(timestamps)).isoformat()
                } if timestamps else None
            }
        
        return summary
    
    def get_error_analysis(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """
        Analyze errors and warnings in the logs
        
        Returns:
            Dictionary with error/warning statistics by feature and module
        """
        error_logs = [log for log in logs if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]]
        warning_logs = [log for log in logs if log.level == LogLevel.WARNING]
        
        return {
            "error_count": len(error_logs),
            "warning_count": len(warning_logs),
            "errors_by_feature": Counter(log.feature_tag for log in error_logs),
            "errors_by_module": Counter(log.module_tag for log in error_logs),
            "warnings_by_feature": Counter(log.feature_tag for log in warning_logs),
            "warnings_by_module": Counter(log.module_tag for log in warning_logs),
            "error_functions": Counter(log.function_name for log in error_logs),
            "recent_errors": [log.to_dict() for log in sorted(error_logs, 
                                                              key=lambda x: x.timestamp, 
                                                              reverse=True)[:10]]
        }
    
    def get_performance_metrics(self, logs: List[LogEntry]) -> Dict[str, Any]:
        """
        Calculate performance metrics from logs
        
        Looks for logs with 'duration' or 'elapsed_time' parameters
        """
        perf_logs = []
        for log in logs:
            if 'duration' in log.parameters or 'elapsed_time' in log.parameters:
                duration = log.parameters.get('duration', log.parameters.get('elapsed_time'))
                if isinstance(duration, (int, float)):
                    perf_logs.append((log, duration))
        
        if not perf_logs:
            return {"message": "No performance data found in logs"}
        
        durations = [duration for _, duration in perf_logs]
        
        # Group by function
        func_durations = defaultdict(list)
        for log, duration in perf_logs:
            func_durations[log.function_name].append(duration)
        
        func_stats = {}
        for func, dur_list in func_durations.items():
            func_stats[func] = {
                "avg": statistics.mean(dur_list),
                "min": min(dur_list),
                "max": max(dur_list),
                "count": len(dur_list),
                "total": sum(dur_list)
            }
        
        return {
            "total_operations": len(perf_logs),
            "avg_duration": statistics.mean(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "total_duration": sum(durations),
            "by_function": func_stats,
            "slowest_operations": [
                {
                    "function": log.function_name,
                    "feature": log.feature_tag,
                    "module": log.module_tag,
                    "duration": duration,
                    "timestamp": log.formatted_timestamp
                }
                for log, duration in sorted(perf_logs, 
                                           key=lambda x: x[1], 
                                           reverse=True)[:10]
            ]
        }
    
    def generate_report(self, 
                       logs: List[LogEntry],
                       include_summary: bool = True,
                       include_errors: bool = True,
                       include_performance: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report
        
        Args:
            logs: Log entries to analyze
            include_summary: Include feature/module summaries
            include_errors: Include error analysis
            include_performance: Include performance metrics
        
        Returns:
            Comprehensive report dictionary
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_logs": len(logs),
            "time_range": {
                "start": datetime.fromtimestamp(min(log.timestamp for log in logs)).isoformat(),
                "end": datetime.fromtimestamp(max(log.timestamp for log in logs)).isoformat()
            } if logs else None
        }
        
        if include_summary:
            report["feature_summary"] = self.get_feature_summary(logs)
            report["module_summary"] = self.get_module_summary(logs)
        
        if include_errors:
            report["error_analysis"] = self.get_error_analysis(logs)
        
        if include_performance:
            report["performance_metrics"] = self.get_performance_metrics(logs)
        
        return report


class LogViewer:
    """
    Interactive viewer for logs with filtering and display options
    """
    
    def __init__(self, analyzer: LogAnalyzer):
        self.analyzer = analyzer
    
    def display_feature_view(self, 
                            logs: List[LogEntry],
                            feature_tag: Optional[str] = None,
                            max_entries: int = 50) -> None:
        """
        Display logs organized by feature
        
        Args:
            logs: Log entries to display
            feature_tag: Optional specific feature to display
            max_entries: Maximum entries to show per feature
        """
        feature_groups = self.analyzer.group_by_feature(logs)
        
        if feature_tag:
            if feature_tag in feature_groups:
                self._display_feature_section(feature_tag, 
                                            feature_groups[feature_tag], 
                                            max_entries)
            else:
                print(f"No logs found for feature: {feature_tag}")
        else:
            for feature, feature_logs in sorted(feature_groups.items()):
                self._display_feature_section(feature, feature_logs, max_entries)
    
    def display_module_view(self,
                           logs: List[LogEntry],
                           module_tag: Optional[str] = None,
                           max_entries: int = 50) -> None:
        """
        Display logs organized by module
        
        Args:
            logs: Log entries to display
            module_tag: Optional specific module to display
            max_entries: Maximum entries to show per module
        """
        module_groups = self.analyzer.group_by_module(logs)
        
        if module_tag:
            if module_tag in module_groups:
                self._display_module_section(module_tag, 
                                           module_groups[module_tag], 
                                           max_entries)
            else:
                print(f"No logs found for module: {module_tag}")
        else:
            for module, module_logs in sorted(module_groups.items()):
                self._display_module_section(module, module_logs, max_entries)
    
    def _display_feature_section(self, 
                                feature: str, 
                                logs: List[LogEntry], 
                                max_entries: int) -> None:
        """Display a feature section"""
        print(f"\n{'='*80}")
        print(f"FEATURE: {feature} ({len(logs)} entries)")
        print(f"{'='*80}")
        
        # Show summary
        modules = set(log.module_tag for log in logs)
        level_counts = Counter(log.level.value for log in logs)
        
        print(f"Modules involved: {', '.join(sorted(modules))}")
        print(f"Log levels: {dict(level_counts)}")
        print("")
        
        # Show recent logs
        sorted_logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)
        for log in sorted_logs[:max_entries]:
            print(f"  {log.to_formatted_string()}")
    
    def _display_module_section(self,
                               module: str,
                               logs: List[LogEntry],
                               max_entries: int) -> None:
        """Display a module section"""
        print(f"\n{'='*80}")
        print(f"MODULE: {module} ({len(logs)} entries)")
        print(f"{'='*80}")
        
        # Show summary
        features = set(log.feature_tag for log in logs)
        level_counts = Counter(log.level.value for log in logs)
        
        print(f"Features using this module: {', '.join(sorted(features))}")
        print(f"Log levels: {dict(level_counts)}")
        print("")
        
        # Show recent logs
        sorted_logs = sorted(logs, key=lambda x: x.timestamp, reverse=True)
        for log in sorted_logs[:max_entries]:
            print(f"  {log.to_formatted_string()}")