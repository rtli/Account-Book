import { useState, useEffect, useCallback } from 'react';
import {
  Card, Form, Input, InputNumber, Select, DatePicker, Button, Table, message, Space, Tag,
} from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { spendingApi, categoryApi, type Spending, type Category } from '../services/api';

export default function HomePage() {
  const [form] = Form.useForm();
  const [categories, setCategories] = useState<Category[]>([]);
  const [recentItems, setRecentItems] = useState<Spending[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const loadCategories = useCallback(async () => {
    try {
      const res = await categoryApi.list();
      setCategories(res.data.filter((c) => c.level === 2));
    } catch { /* ignore */ }
  }, []);

  const loadRecent = useCallback(async () => {
    setLoading(true);
    try {
      const res = await spendingApi.list({ page: 1, page_size: 10 });
      setRecentItems(res.data.items);
    } catch { /* ignore */ }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadCategories();
    loadRecent();
  }, [loadCategories, loadRecent]);

  const handleSubmit = async (values: any) => {
    setSubmitting(true);
    try {
      await spendingApi.create({
        item_name: values.item_name,
        category_id: values.category_id,
        amount: values.amount,
        spend_date: values.spend_date?.format('YYYY-MM-DD'),
      });
      message.success('记账成功！');
      form.resetFields();
      loadRecent();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '记账失败');
    }
    setSubmitting(false);
  };

  const handleDelete = async (id: number) => {
    try {
      await spendingApi.delete(id);
      message.success('已删除');
      loadRecent();
    } catch {
      message.error('删除失败');
    }
  };

  const columns = [
    { title: '品名', dataIndex: 'item_name', key: 'item_name' },
    {
      title: '分类',
      dataIndex: 'category_name',
      key: 'category_name',
      render: (text: string) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (val: number) => (
        <span className="ledger-amount" style={{ color: 'var(--danger)', fontSize: 13.5 }}>
          ¥{val.toFixed(2)}
        </span>
      ),
    },
    { title: '日期', dataIndex: 'spend_date', key: 'spend_date' },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Spending) => (
        <Button type="link" danger size="small" onClick={() => handleDelete(record.id)}>
          删除
        </Button>
      ),
    },
  ];

  return (
    <div>
      <header style={{ marginBottom: 28, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between', gap: 24 }}>
        <div>
          <h1 style={{ fontSize: 26, fontWeight: 600, letterSpacing: '-0.02em', lineHeight: 1.2 }}>
            记一笔
          </h1>
          <p style={{ marginTop: 6, marginBottom: 0, color: 'var(--fg-2)', fontSize: 14 }}>
            快速录入一条支出，右侧为最近 10 条记录。
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--fg-3)', fontSize: 12 }}>
          <span>提交</span>
          <span className="ledger-kbd">↵</span>
        </div>
      </header>
      <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
      <Card title="快速记账" style={{ flex: '1 1 360px', minWidth: 360 }}>
        <Form form={form} layout="vertical" onFinish={handleSubmit}
          initialValues={{ spend_date: dayjs() }}>
          <Form.Item name="item_name" label="品名" rules={[{ required: true, message: '请输入品名' }]}>
            <Input placeholder="在此输入品名" maxLength={50} />
          </Form.Item>
          <Form.Item name="category_id" label="分类" rules={[{ required: true, message: '请选择分类' }]}>
            <Select placeholder="选择分类" showSearch optionFilterProp="label"
              options={categories.map((c) => ({ value: c.id, label: c.name }))} />
          </Form.Item>
          <Form.Item name="amount" label="金额" rules={[{ required: true, message: '请输入金额' }]}>
            <InputNumber placeholder="在此输入金额" min={0.01} step={0.01}
              style={{ width: '100%' }} prefix="¥" />
          </Form.Item>
          <Form.Item name="spend_date" label="日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" icon={<PlusOutlined />}
              loading={submitting} block size="large">
              记一笔
            </Button>
          </Form.Item>
        </Form>
      </Card>

      <Card title="最近记录" style={{ flex: '2 1 500px', minWidth: 400 }}>
        <Table columns={columns} dataSource={recentItems} rowKey="id"
          loading={loading} pagination={false} size="middle" />
      </Card>
      </div>
    </div>
  );
}
