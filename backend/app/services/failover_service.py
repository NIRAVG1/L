class FailoverService:
    SUPPORTED_STATUSES={429,500,502,503}
    def parse_simulation(self, header):
        parsed={}
        if not header: return parsed
        for item in header.split(','):
            try:
                key,status=item.strip().split('=',1); status=int(status)
                if (key=='*' or key.startswith('key_')) and status in self.SUPPORTED_STATUSES: parsed[key]=status
            except (ValueError,TypeError): continue
        return parsed
    @staticmethod
    def should_skip(simulation,key_id): return bool(simulation.get('*') or simulation.get(key_id))
failover_service=FailoverService()
