import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class DriftDetector:
    def __init__(self):
        """Initialize the drift detector"""
        self.baselines = {}
        self.data_dir = Path(__file__).resolve().parent / "sample_data"
        self.load_baselines()
    
    def load_baselines(self):
        """Load baseline configurations from JSON file"""
        baseline_path = self.data_dir / "baseline_configs.json"
        try:
            with baseline_path.open("r", encoding="utf-8") as file:
                records = [json.loads(line) for line in file if line.strip()]
        except (FileNotFoundError, json.JSONDecodeError) as error:
            print(f"⚠️ Could not load {baseline_path}: {error}")
            self.create_default_baselines()
            return

        self.baselines = {
            record["control_id"]: record
            for record in records
            if isinstance(record, dict) and record.get("control_id")
        }
        if not self.baselines:
            print("⚠️ No valid baselines found; using defaults")
            self.create_default_baselines()
            return
        print(f"✅ Loaded {len(self.baselines)} baselines")
    
    def create_default_baselines(self):
        """Create default baselines"""
        self.baselines = {
            "Control-68": {
                "name": "Cloud Security",
                "type": "cloud",
                "expected": "enabled=True",
                "risk_level": "HIGH",
                "compliance": ["NIST SI-12", "GDPR Art 32"],
                "remediation": "Re-enable cloud security controls",
                "severity_score": 85
            },
            "Control-78": {
                "name": "Network Segmentation",
                "type": "network",
                "expected": "enabled=False",
                "risk_level": "MEDIUM",
                "compliance": ["NIST AC-17"],
                "remediation": "Verify network segmentation",
                "severity_score": 65
            },
            "Control-94": {
                "name": "Network Security",
                "type": "network",
                "expected": "enabled=False",
                "risk_level": "MEDIUM",
                "compliance": ["NIST AC-17"],
                "remediation": "Review network security rules",
                "severity_score": 70
            }
        }
    
    def load_data(self):
        """Load drift events from CSV file"""
        csv_path = self.data_dir / "config_drift_events.csv"
        try:
            df = pd.read_csv(csv_path)
        except (FileNotFoundError, pd.errors.ParserError) as error:
            print(f"⚠️ Could not load {csv_path}: {error}")
            return self.create_sample_data()

        print(f"✅ Loaded {len(df)} events")
        print(f"📊 Columns: {df.columns.tolist()}")
        return df

    def load_drift_events(self):
        """Alias for load_data"""
        return self.load_data()
    
    def create_sample_data(self):
        """Create sample data"""
        return pd.DataFrame([
            {'control_name': 'Control-78', 'current_value': 'enabled=False', 'baseline_value': 'enabled=False',
             'change_date': '2025-04-20', 'operator_name': 'engineer', 'status': 'Mitigated'},
            {'control_name': 'Control-68', 'current_value': 'enabled=True', 'baseline_value': 'enabled=False',
             'change_date': '2025-04-20', 'operator_name': 'admin', 'status': 'Under_Review'}
        ])
    
    def detect_drifts(self, df):
        """Detect configuration drifts from your CSV"""
        drifts = []
        
        print(f"\n🔍 Checking {len(df)} events for drifts...")
        
        for _, row in df.iterrows():
            # Use control_name as the identifier
            control_name = row.get('control_name')
            if pd.isna(control_name) or not str(control_name).strip():
                continue
            
            # Get current and baseline values
            current_value = str(row.get('current_value', '')).strip()
            baseline_value = str(row.get('baseline_value', '')).strip()
            
            # A drift exists if current != baseline
            if current_value != baseline_value:
                # Determine risk level based on severity column or defaults
                risk_level, risk_score = self._risk_from_severity(row.get('severity'))
                
                # Get additional info
                change_type = row.get('change_type', 'Unknown')
                change_type = 'Unknown' if pd.isna(change_type) else str(change_type)
                change_date = row.get('change_date', 'Unknown')
                operator = row.get('operator_name', row.get('operator_email', 'Unknown'))
                operator = 'Unknown' if pd.isna(operator) else str(operator)
                status = row.get('status', 'Unknown')
                status = 'Unknown' if pd.isna(status) else str(status)
                
                # Check if approved (based on status or approver fields)
                approver = row.get('approver_name', row.get('approver_email', ''))
                approved = bool(pd.notna(approver) and approver != '')
                
                # If status is Under_Review or Open, treat as not approved
                if status.lower() in {'under_review', 'open', 'pending'}:
                    approved = False
                
                # Get compliance impact
                compliance = row.get('compliance_impact', 'GDPR')
                if pd.isna(compliance) or not str(compliance).strip():
                    compliance = 'NIST'
                compliance = self._normalize_compliance(compliance)
                
                # Create drift record
                drifts.append({
                    'control_id': control_name,
                    'name': row.get('control_name', control_name),
                    'control_type': (
                        'Unknown'
                        if pd.isna(row.get('control_type', 'Unknown'))
                        else str(row.get('control_type', 'Unknown'))
                    ),
                    'current': current_value,
                    'expected': baseline_value,
                    'risk_level': risk_level,
                    'duration_days': self._calculate_duration(change_date),
                    'timestamp': change_date,
                    'changed_by': operator,
                    'approved': approved,
                    'compliance': [str(compliance)],
                    'remediation': self._get_remediation(control_name, change_type),
                    'risk_score': risk_score,
                    'change_type': change_type,
                    'status': status
                })
        
        # Sort by risk score
        drifts.sort(key=lambda x: x['risk_score'], reverse=True)
        print(f"✅ Detected {len(drifts)} drifts")
        
        if drifts:
            print("\n📋 Sample drifts found:")
            for d in drifts[:3]:
                print(f"  - {d['control_id']}: {d['current']} vs {d['expected']} (Risk: {d['risk_score']})")
        
        return drifts
    
    def _calculate_duration(self, change_date):
        """Calculate days since change"""
        if change_date == 'Unknown' or pd.isna(change_date):
            return 30  # Default duration

        try:
            change_dt = pd.to_datetime(change_date, errors="raise")
            duration = (datetime.now() - change_dt.to_pydatetime()).days
            return max(1, duration)
        except (TypeError, ValueError, OverflowError):
            return 30

    def _risk_from_severity(self, severity):
        """Normalize source severity while preserving the UI's risk levels."""
        normalized = str(severity or "MEDIUM").strip().upper()
        scores = {
            "CRITICAL": ("CRITICAL", 95),
            "HIGH": ("HIGH", 80),
            "MEDIUM": ("MEDIUM", 60),
            "LOW": ("LOW", 30),
            "INFO": ("LOW", 15),
        }
        return scores.get(normalized, ("MEDIUM", 60))

    def _normalize_compliance(self, compliance):
        """Recover common framework abbreviations from the sample CSV."""
        normalized = str(compliance).strip().upper()
        return {
            "IS": "ISO",
            "GD": "GDPR",
            "NI": "NIST",
            "PC": "PCI",
            "CI": "CIS",
        }.get(normalized, normalized)
    
    def _get_remediation(self, control_name, change_type):
        """Generate remediation steps"""
        remediation_map = {
            'Policy Change': f'Review and rollback policy change for {control_name}',
            'Performance Tuning': f'Verify if performance tuning is still needed for {control_name}',
            'Emergency Fix': f'Validate emergency fix and create permanent solution for {control_name}',
            'Maintenance': f'Ensure maintenance changes were properly documented for {control_name}'
        }
        return remediation_map.get(change_type, f'Review and remediate {control_name} configuration')
    
    def get_summary(self, drifts):
        """Generate summary statistics"""
        if not drifts:
            return {
                'total_drifts': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'avg_risk_score': 0,
                'by_type': {},
                'compliance_impact': {}
            }
        
        by_type = {}
        compliance_impact = {}
        
        for d in drifts:
            t = d['control_type']
            by_type[t] = by_type.get(t, 0) + 1
            for comp in d['compliance']:
                compliance_impact[comp] = compliance_impact.get(comp, 0) + 1
        
        return {
            'total_drifts': len(drifts),
            'critical': len([d for d in drifts if d['risk_level'] == 'CRITICAL']),
            'high': len([d for d in drifts if d['risk_level'] == 'HIGH']),
            'medium': len([d for d in drifts if d['risk_level'] == 'MEDIUM']),
            'low': len([d for d in drifts if d['risk_level'] == 'LOW']),
            'avg_risk_score': sum(d['risk_score'] for d in drifts) // len(drifts) if drifts else 0,
            'by_type': by_type,
            'compliance_impact': compliance_impact
        }

if __name__ == "__main__":
    print("=" * 60)
    print("DRIFT DETECTOR - TEST WITH YOUR DATA")
    print("=" * 60)
    
    detector = DriftDetector()
    df = detector.load_data()
    drifts = detector.detect_drifts(df)
    summary = detector.get_summary(drifts)
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total drifts: {summary['total_drifts']}")
    print(f"Critical: {summary['critical']}")
    print(f"High: {summary['high']}")
    print(f"Medium: {summary['medium']}")
    print(f"Avg Risk Score: {summary['avg_risk_score']}")