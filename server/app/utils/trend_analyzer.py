import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from collections import defaultdict

class TrendAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=3, random_state=42)

    def analyze_trends(self, exam_data):
        if not exam_data:
            return []

        # Prepare data for analysis
        study_hours = np.array([d['study_hours'] for d in exam_data]).reshape(-1, 1)
        grades = np.array([d['grade'] for d in exam_data]).reshape(-1, 1)

        # Scale the data
        X = np.hstack([study_hours, grades])
        X_scaled = self.scaler.fit_transform(X)

        # Perform clustering
        clusters = self.kmeans.fit_predict(X_scaled)

        # Analyze trends
        trends = defaultdict(list)
        for i, data in enumerate(exam_data):
            cluster = clusters[i]
            trends[data['subject']].append({
                'topic': data['topic'],
                'grade': data['grade'],
                'study_hours': data['study_hours'],
                'cluster': int(cluster)
            })

        # Generate insights
        insights = []
        for subject, data in trends.items():
            avg_grade = np.mean([d['grade'] for d in data])
            avg_hours = np.mean([d['study_hours'] for d in data])
            
            # Find most effective study patterns
            high_performers = [d for d in data if d['grade'] > avg_grade]
            if high_performers:
                optimal_hours = np.mean([d['study_hours'] for d in high_performers])
                insights.append({
                    'subject': subject,
                    'avg_grade': float(avg_grade),
                    'avg_study_hours': float(avg_hours),
                    'optimal_study_hours': float(optimal_hours),
                    'topics': list(set(d['topic'] for d in data)),
                    'recommendation': f"For {subject}, studying around {optimal_hours:.1f} hours tends to yield better results"
                })

        return insights 