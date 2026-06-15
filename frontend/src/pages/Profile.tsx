import { Button, Form, Input, InputNumber, Statistic, TimePicker } from 'antd';
import { useEffect } from 'react';
import { AvatarUploader } from '../components/common/AvatarUploader';
import { EmptyState } from '../components/common/EmptyState';
import { useAuth } from '../hooks/useAuth';
import { useUserStore } from '../stores/userStore';
import dayjs from 'dayjs';

export function Profile() {
  const { token, user, logout } = useAuth();
  const { report, loadReport, updateProfile } = useUserStore();
  const [form] = Form.useForm();

  useEffect(() => {
    if (token) loadReport();
  }, [token, loadReport]);

  const profile = report?.user || user;

  useEffect(() => {
    if (profile) {
      form.setFieldsValue({
        ...profile,
        meditation_reminder_time: profile.meditation_reminder_time
          ? dayjs(profile.meditation_reminder_time, 'HH:mm:ss')
          : null,
      });
    }
  }, [profile, form]);

  const handleFinish = (values: any) => {
    const payload = {
      ...values,
      meditation_reminder_time: values.meditation_reminder_time
        ? values.meditation_reminder_time.format('HH:mm:ss')
        : null,
    };
    updateProfile(payload);
  };

  return (
    <main className="page">
      <h1 className="page-title">个人中心</h1>
      <p className="page-kicker">维护个人资料，并查看情绪、测评和日记的心理报告汇总。</p>

      {profile ? (
        <section className="grid two">
          <div className="panel profile-band">
            <AvatarUploader user={profile} onChange={(avatar) => updateProfile({ avatar })} />
            <Form
              form={form}
              layout="vertical"
              initialValues={profile}
              onFinish={handleFinish}
            >
              <Form.Item name="nickname" label="昵称">
                <Input />
              </Form.Item>
              <Form.Item name="gender" label="性别">
                <Input />
              </Form.Item>
              <h3 style={{ marginTop: 16, marginBottom: 8 }}>冥想练习计划</h3>
              <Form.Item name="meditation_days_per_week" label="每周练习天数" rules={[{ required: true }]}>
                <InputNumber min={1} max={7} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="meditation_reminder_time" label="每日提醒时间">
                <TimePicker format="HH:mm" style={{ width: '100%' }} allowClear />
              </Form.Item>
              <Button type="primary" htmlType="submit">保存资料</Button>
              <Button style={{ marginLeft: 8 }} onClick={logout}>退出</Button>
            </Form>
          </div>
          <div className="panel">
            <h2>心理报告汇总</h2>
            <div className="grid three">
              <Statistic title="平均情绪" value={report?.avg_mood || 0} />
              <Statistic title="测评次数" value={report?.assessment_count || 0} />
              <Statistic title="日记篇数" value={report?.journal_count || 0} />
            </div>
            <h3 style={{ marginTop: 20 }}>本周冥想进度</h3>
            <div className="grid three">
              <Statistic
                title="已完成"
                value={report?.meditation_week_completed || 0}
                suffix={`/ ${report?.meditation_week_target || 0} 天`}
              />
              <Statistic
                title="达成率"
                value={report?.meditation_week_completion_rate || 0}
                suffix="%"
              />
              <Statistic title="目标天数" value={report?.meditation_week_target || 0} suffix="天" />
            </div>
            <div
              style={{
                marginTop: 12,
                height: 8,
                background: '#f0f0f0',
                borderRadius: 4,
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${Math.min(report?.meditation_week_completion_rate || 0, 100)}%`,
                  background: 'linear-gradient(90deg, #52c41a, #73d13d)',
                  borderRadius: 4,
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
          </div>
        </section>
      ) : (
        <EmptyState title="未获取到用户资料" description="请确认后端认证接口可用。" />
      )}
    </main>
  );
}

