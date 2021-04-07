from src.model_monitor import ModelQualityMonitor

if __name__ == '__main__':
    model_quality_monitor = ModelQualityMonitor()
    model_quality_monitor.suggest_baseline()
    model_quality_monitor.create_monitoring_schedule()
