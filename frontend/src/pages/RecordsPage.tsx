import { useState, useEffect, useCallback } from 'react';
import {
  Card, Table, Input, Select, DatePicker, Space, Button, Tag, Popconfirm, message, Modal, Form, InputNumber,
} from 'antd';
import type { TablePaginationConfig } from 'antd';
import type { ColumnsType, SorterResult } from 'antd/es/table/interface';
import { SearchOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { spendingApi, categoryApi, type Spending, type Category } from '../services/api';

const { RangePicker } = DatePicker;

type SortOrder = 'asc' | 'desc';
const DEFAULT_SORT_BY = 'spend_date';
const DEFAULT_SORT_ORDER: SortOrder = 'desc';

export default function RecordsPage() {
  const [data, setData] = useState<Spending[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState<Category[]>([]);
  const [keyword, setKeyword] = useState('');
  const [categoryId, setCategoryId] = useState<number | undefined>();
  const [dateRange, setDateRange] = useState<[string, string] | null>(null);
  const [sortBy, setSortBy] = useState<string>(DEFAULT_SORT_BY);
  const [sortOrder, setSortOrder] = useState<SortOrder>(DEFAULT_SORT_ORDER);
  const [editModal, setEditModal] = useState(false);
  const [editingItem, setEditingItem] = useState<Spending | null>(null);
  const [editForm] = Form.useForm();

  const loadCategories = useCallback(async () => {
    try {
      const res = await categoryApi.list();
      setCategories(res.data.filter((c) => c.level === 2));
    } catch { /* ignore */ }
  }, []);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await spendingApi.list({
        page,
        page_size: pageSize,
        keyword: keyword || undefined,
        category_id: categoryId,
        start_date: dateRange?.[0],
        end_date: dateRange?.[1],
        sort_by: sortBy,
        order: sortOrder,
      });
      setData(res.data.items);
      setTotal(res.data.total);
    } catch { /* ignore */ }
    setLoading(false);
  }, [page, pageSize, keyword, categoryId, dateRange, sortBy, sortOrder]);

  useEffect(() => { loadCategories(); }, [loadCategories]);
  useEffect(() => { loadData(); }, [loadData]);

  const handleDelete = async (id: number) => {
    await spendingApi.delete(id);
    message.success('已删除');
    loadData();
  };

  const handleEdit = (record: Spending) => {
    setEditingItem(record);
    editForm.setFieldsValue({
      item_name: record.item_name,
      category_id: record.category_id,
      amount: record.amount,
      spend_date: dayjs(record.spend_date),
    });
    setEditModal(true);
  };

  const handleEditSubmit = async () => {
    const values = await editForm.validateFields();
    if (!editingItem) return;
    try {
      await spendingApi.update(editingItem.id, {
        item_name: values.item_name,
        category_id: values.category_id,
        amount: values.amount,
        spend_date: values.spend_date?.format('YYYY-MM-DD'),
      });
      message.success('修改成功');
      setEditModal(false);
      loadData();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '修改失败');
    }
  };

  const columns: ColumnsType<Spending> = [
    {
      title: '品名', dataIndex: 'item_name', key: 'item_name',
      sorter: true,
      sortOrder: sortBy === 'item_name' ? (sortOrder === 'asc' ? 'ascend' : 'descend') : null,
    },
    {
      title: '分类', dataIndex: 'category_name', key: 'category_name',
      render: (text: string) => <Tag color="blue">{text}</Tag>,
    },
    {
      title: '金额', dataIndex: 'amount', key: 'amount',
      render: (val: number) => <span style={{ color: '#f5222d', fontWeight: 500 }}>¥{val.toFixed(2)}</span>,
      sorter: true,
      sortOrder: sortBy === 'amount' ? (sortOrder === 'asc' ? 'ascend' : 'descend') : null,
    },
    {
      title: '日期', dataIndex: 'spend_date', key: 'spend_date',
      sorter: true,
      sortOrder: sortBy === 'spend_date' ? (sortOrder === 'asc' ? 'ascend' : 'descend') : null,
      defaultSortOrder: 'descend' as const,
    },
    {
      title: '操作', key: 'action', width: 120,
      render: (_: any, record: Spending) => (
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Popconfirm title="确定删除?" onConfirm={() => handleDelete(record.id)}>
            <Button type="link" danger size="small" icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const handleTableChange = (
    pagination: TablePaginationConfig,
    _filters: Record<string, unknown>,
    sorter: SorterResult<Spending> | SorterResult<Spending>[],
  ) => {
    const next = Array.isArray(sorter) ? sorter[0] : sorter;
    const rawOrder = next?.order;

    // Third click on a column header clears the sort; fall back to the default
    // sort so the user can always return to the initial state via UI.
    if (!rawOrder) {
      if (sortBy !== DEFAULT_SORT_BY || sortOrder !== DEFAULT_SORT_ORDER) {
        setSortBy(DEFAULT_SORT_BY);
        setSortOrder(DEFAULT_SORT_ORDER);
        setPage(1);
      }
      return;
    }

    const nextSortBy = (next?.field as string) || DEFAULT_SORT_BY;
    const nextSortOrder: SortOrder = rawOrder === 'ascend' ? 'asc' : 'desc';
    // Reset to page 1 when sort changes so the user sees the new top of the dataset.
    if (nextSortBy !== sortBy || nextSortOrder !== sortOrder) {
      setSortBy(nextSortBy);
      setSortOrder(nextSortOrder);
      setPage(1);
      return;
    }
    if (pagination.current) setPage(pagination.current);
    if (pagination.pageSize) setPageSize(pagination.pageSize);
  };

  return (
    <Card title="账目列表">
      <Space wrap style={{ marginBottom: 16 }}>
        <Input placeholder="搜索品名" prefix={<SearchOutlined />} allowClear
          style={{ width: 200 }} onPressEnter={(e: any) => { setKeyword(e.target.value); setPage(1); }}
          onChange={(e) => { if (!e.target.value) { setKeyword(''); setPage(1); } }} />
        <Select placeholder="筛选分类" allowClear style={{ width: 160 }}
          options={categories.map((c) => ({ value: c.id, label: c.name }))}
          onChange={(val) => { setCategoryId(val); setPage(1); }} />
        <RangePicker onChange={(_, dateStrings) => {
          setDateRange(dateStrings[0] ? [dateStrings[0], dateStrings[1]] : null);
          setPage(1);
        }} />
      </Space>

      <Table columns={columns} dataSource={data} rowKey="id" loading={loading}
        onChange={handleTableChange}
        pagination={{
          current: page, pageSize, total, showSizeChanger: true,
          showTotal: (t) => `共 ${t} 条`,
        }} />

      <Modal title="编辑账目" open={editModal} onOk={handleEditSubmit}
        onCancel={() => setEditModal(false)} okText="保存" cancelText="取消">
        <Form form={editForm} layout="vertical">
          <Form.Item name="item_name" label="品名" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="category_id" label="分类" rules={[{ required: true }]}>
            <Select options={categories.map((c) => ({ value: c.id, label: c.name }))} />
          </Form.Item>
          <Form.Item name="amount" label="金额" rules={[{ required: true }]}>
            <InputNumber min={0.01} step={0.01} style={{ width: '100%' }} prefix="¥" />
          </Form.Item>
          <Form.Item name="spend_date" label="日期">
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
}
