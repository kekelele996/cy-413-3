import { Button, List, Statistic, Tag, message } from 'antd';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AssessmentCard } from '../components/common/AssessmentCard';
import { EmptyState } from '../components/common/EmptyState';
import { MoodSelector } from '../components/common/MoodSelector';
import { MoodTrendChart } from '../components/common/MoodTrendChart';
import { getAssessments } from '../api/assessment';
import { completeMeditation, getMeditationToday } from '../api/journal';
import { useAuth } from '../hooks/useAuth';
import { useMoodStats } from '../hooks/useMoodStats';
import { useMoodStore } from '../stores/moodStore';
import { useUserStore } from '../stores/userStore';
import type { Assessment } from '../types';
import { CheckCircleOutlined, PlayCircleOutlined } from '@ant-design/icons';

export function Dashboard() {
  const { token } = useAuth();
  const { moods, trend, loadMoods, loadTrend, createMood } = useMoodStore();
  const { report, loadReport } = useUserStore();
  const stats = useMoodStats(moods);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [meditationCompleted, setMeditationCompleted] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) return;
    loadMoods();
    loadTrend();
    loadReport();
    getAssessments().then((items) => setAssessments(items.slice(0, 2))).catch(() => setAssessments([]));
    getMeditationToday().then((res) => setMeditationCompleted(res.completed)).catch(() => setMeditationCompleted(false));
  }, [token, loadMoods, loadTrend, loadReport]);

  const handleCompleteMeditation = async () => {
    setLoading(true);
    try {
      await completeMeditation();
      setMeditationCompleted(true);
      loadReport();
      message.success('恭喜完成今日冥想！');
    } catch (e: any) {
      message.error(e?.message || '完成冥想失败');
    } finally {
      setLoading(false);
    }
  };

  const targetDays = report?.meditation_week_target || 3;
  const completedDays = report?.meditation_week_completed || 0;

  return (
    <main className="page">
      <h1 className="page-title">心情花园</h1>
      <p className="page-kicker">用每日情绪、测评和日记把心理状态从模糊感受变成可以观察的线索。</p>

      <section className="grid three" style={{ marginBottom: 18 }}>
        <div className="panel">
          <Statistic title="平均情绪" value={stats.avgMood} suffix="/ 10" />
        </div>
        <div className="panel">
          <Statistic title="记录次数" value={stats.total} />
        </div>
        <div className="panel">
          <Statistic title="主要标签" value={stats.dominantTag} />
        </div>
      </section>

      <section className="panel" style={{ marginBottom: 18 }}>
        <div className="toolbar">
          <h2>今日冥想练习</h2>
          <Tag color={meditationCompleted ? 'success' : 'processing'}>
            {meditationCompleted ? '已完成' : '待完成'}
          </Tag>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, padding: '12px 0' }}>
          <div style={{ flex: 1 }}>
            <h3 style={{ margin: '0 0 8px 0' }}>
              {meditationCompleted ? '今日冥想已完成 🎉' : '今天的冥想练习还没开始哦'}
            </h3>
            <p className="muted" style={{ margin: '0 0 12px 0' }}>
              本周目标：{targetDays} 天 · 已完成：{completedDays} 天 · 达成率：{report?.meditation_week_completion_rate || 0}%
            </p>
            <div
              style={{
                height: 6,
                background: '#f0f0f0',
                borderRadius: 3,
                overflow: 'hidden',
                marginBottom: 12,
              }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${Math.min((completedDays / targetDays) * 100, 100)}%`,
                  background: 'linear-gradient(90deg, #52c41a, #73d13d)',
                  borderRadius: 3,
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
            {!meditationCompleted && (
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleCompleteMeditation}
                loading={loading}
              >
                开始今日冥想（10 分钟）
              </Button>
            )}
            {meditationCompleted && (
              <Button icon={<CheckCircleOutlined />} disabled>
                今日已完成
              </Button>
            )}
          </div>
        </div>
      </section>

      <section className="grid two">
        <div className="panel">
          <h2>本周情绪曲线</h2>
          {trend.length ? <MoodTrendChart data={trend} /> : <EmptyState title="暂无曲线" description="记录一次心情后会生成趋势。" />}
        </div>
        <div className="panel">
          <h2>快速记录</h2>
          <MoodSelector compact onSubmit={createMood} />
        </div>
      </section>

      <section style={{ marginTop: 18 }} className="panel">
        <div className="toolbar">
          <h2>最新测评推荐</h2>
          <Button>
            <Link to="/assessments">查看全部</Link>
          </Button>
        </div>
        {assessments.length ? (
          <List
            grid={{ gutter: 16, column: 2 }}
            dataSource={assessments}
            renderItem={(assessment) => (
              <List.Item>
                <AssessmentCard assessment={assessment} onStart={() => { location.href = '/assessments'; }} />
              </List.Item>
            )}
          />
        ) : (
          <EmptyState title="暂无测评" description="后端初始化后会写入焦虑和睡眠测评。" />
        )}
      </section>
    </main>
  );
}

