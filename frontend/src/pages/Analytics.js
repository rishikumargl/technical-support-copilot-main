import React, { useState, useEffect } from 'react';
import { FiLoader, FiRefreshCw } from 'react-icons/fi';
import { getSystemStats, getFeedbackAnalytics } from '../api/ragApi';
import './Analytics.css';

function Analytics() {
  const [stats, setStats] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const [statsData, feedbackData] = await Promise.all([
        getSystemStats(),
        getFeedbackAnalytics(),
      ]);
      setStats(statsData);
      setFeedback(feedbackData);
    } catch (error) {
      console.error('Analytics error:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, unit = '', subtitle = '' }) => (
    <div className="stat-card">
      <h4>{title}</h4>
      <div className="stat-value">
        {value}
        {unit && <span className="unit">{unit}</span>}
      </div>
      {subtitle && <p className="subtitle">{subtitle}</p>}
    </div>
  );

  return (
    <div className="analytics">
      <div className="analytics-header">
        <h2>System Analytics & Performance</h2>
        <button onClick={fetchAnalytics} disabled={loading} className="refresh-btn">
          <FiRefreshCw className={loading ? 'spin' : ''} size={20} />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="loading">
          <FiLoader className="spin" size={24} />
          Loading analytics...
        </div>
      ) : (
        <>
          {stats && (
            <>
              <section className="analytics-section">
                <h3>System Statistics</h3>
                <div className="stats-grid">
                  <StatCard
                    title="Total Documents"
                    value={stats.total_documents || 0}
                    subtitle="in knowledge base"
                  />
                  <StatCard
                    title="Total Chunks"
                    value={stats.total_chunks || 0}
                    subtitle="indexed and searchable"
                  />
                  <StatCard
                    title="Average Chunk Size"
                    value={Math.round(stats.avg_chunk_size || 0)}
                    unit=" tokens"
                  />
                  <StatCard
                    title="Index Size"
                    value={((stats.index_size || 0) / (1024 * 1024)).toFixed(2)}
                    unit=" MB"
                  />
                  <StatCard
                    title="Query Response Time"
                    value={Math.round(stats.avg_response_time || 0)}
                    unit=" ms"
                    subtitle="average"
                  />
                  <StatCard
                    title="System Uptime"
                    value={(stats.uptime_hours || 0).toFixed(1)}
                    unit=" hours"
                  />
                </div>
              </section>

              <section className="analytics-section">
                <h3>Retrieval Strategy Performance</h3>
                <div className="strategies-grid">
                  {stats.retrieval_strategies &&
                    Object.entries(stats.retrieval_strategies).map(([strategy, data]) => (
                      <div key={strategy} className="strategy-card">
                        <h4 className="strategy-name">
                          {strategy.toUpperCase().replace(/_/g, ' ')}
                        </h4>
                        <div className="strategy-metrics">
                          <div className="metric">
                            <span className="label">Accuracy</span>
                            <span className="value">{(data.accuracy || 0).toFixed(2)}%</span>
                          </div>
                          <div className="metric">
                            <span className="label">Precision</span>
                            <span className="value">{(data.precision || 0).toFixed(2)}%</span>
                          </div>
                          <div className="metric">
                            <span className="label">Avg Time</span>
                            <span className="value">{Math.round(data.avg_time || 0)}ms</span>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </section>

              {feedback && (
                <section className="analytics-section">
                  <h3>User Feedback</h3>
                  <div className="feedback-grid">
                    <div className="feedback-card">
                      <h4>Helpful Responses</h4>
                      <div className="feedback-value positive">
                        {feedback.helpful_count || 0}
                      </div>
                      <p className="feedback-percent">
                        {feedback.helpful_percentage || 0}% of feedback
                      </p>
                    </div>
                    <div className="feedback-card">
                      <h4>Unhelpful Responses</h4>
                      <div className="feedback-value negative">
                        {feedback.unhelpful_count || 0}
                      </div>
                      <p className="feedback-percent">
                        {feedback.unhelpful_percentage || 0}% of feedback
                      </p>
                    </div>
                    <div className="feedback-card">
                      <h4>Total Feedback</h4>
                      <div className="feedback-value neutral">
                        {feedback.total_feedback || 0}
                      </div>
                      <p className="feedback-percent">responses rated</p>
                    </div>
                  </div>
                </section>
              )}

              <section className="analytics-section">
                <h3>Document Statistics by Department</h3>
                <div className="departments-grid">
                  {stats.documents_by_department &&
                    Object.entries(stats.documents_by_department).map(
                      ([dept, count]) => (
                        <div key={dept} className="dept-card">
                          <h4>{dept}</h4>
                          <p className="dept-count">{count} documents</p>
                        </div>
                      )
                    )}
                </div>
              </section>
            </>
          )}
        </>
      )}
    </div>
  );
}

export default Analytics;
