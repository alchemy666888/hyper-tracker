class _Counter:
    def labels(self, *args, **kwargs):
        _ = args, kwargs
        return self

    def inc(self):
        return None


class _Gauge:
    def labels(self, *args, **kwargs):
        _ = args, kwargs
        return self

    def set(self, _):
        return None


class Metrics:
    ws_events_total = _Counter()
    ws_reconnections_total = _Counter()
    position_updates_total = _Counter()
    whales_detected_total = _Counter()
    backfill_lag_seconds = _Gauge()
    db_write_duration_seconds = _Counter()
