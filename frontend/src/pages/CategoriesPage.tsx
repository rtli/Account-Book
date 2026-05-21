import { useState, useEffect, useCallback } from 'react';
import {
  Card, Tree, Button, Modal, Form, Input, Select, message, Space, Popconfirm, Empty, Upload,
} from 'antd';
import { PlusOutlined, DeleteOutlined, UploadOutlined, DownloadOutlined } from '@ant-design/icons';
import { categoryApi, type CategoryTree } from '../services/api';

interface TreeNode {
  key: string;
  title: string;
  children?: TreeNode[];
  isLeaf?: boolean;
  categoryId: number;
  level: number;
}

export default function CategoriesPage() {
  const [treeData, setTreeData] = useState<TreeNode[]>([]);
  const [addModal, setAddModal] = useState(false);
  const [addForm] = Form.useForm();
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null);
  const [firstCategories, setFirstCategories] = useState<CategoryTree[]>([]);
  const [importModal, setImportModal] = useState(false);
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<{ imported: number; errors: string[] } | null>(null);

  const loadTree = useCallback(async () => {
    try {
      const res = await categoryApi.tree();
      setFirstCategories(res.data);
      const nodes: TreeNode[] = res.data.map((cat) => ({
        key: `first-${cat.id}`,
        title: cat.name,
        categoryId: cat.id,
        level: 1,
        children: cat.children.map((child) => ({
          key: `second-${child.id}`,
          title: child.name,
          categoryId: child.id,
          level: 2,
          isLeaf: true,
        })),
      }));
      setTreeData(nodes);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { loadTree(); }, [loadTree]);

  const handleAdd = async (values: any) => {
    try {
      await categoryApi.create({
        name: values.name,
        parent_id: values.level === 2 ? values.parent_id : undefined,
        level: values.level,
      });
      message.success('添加成功');
      setAddModal(false);
      addForm.resetFields();
      loadTree();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '添加失败');
    }
  };

  const handleDelete = async () => {
    if (!selectedNode) return;
    try {
      await categoryApi.delete(selectedNode.categoryId);
      message.success('删除成功');
      setSelectedNode(null);
      loadTree();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '删除失败');
    }
  };

  const handleImport = async (file: File) => {
    setImporting(true);
    setImportResult(null);
    try {
      const res = await categoryApi.importCsv(file);
      setImportResult(res.data);
      if (res.data.imported > 0) {
        message.success(`成功导入 ${res.data.imported} 个分类`);
        loadTree();
      }
      if (res.data.errors.length > 0) {
        message.warning(`有 ${res.data.errors.length} 条记录存在问题`);
      }
    } catch (err: any) {
      message.error(err.response?.data?.detail || '导入失败');
    }
    setImporting(false);
  };

  const downloadCategoryTemplate = () => {
    const csv = '\uFEFF二级分类名称,一级分类名称\n早餐,餐饮\n午餐,餐饮\n晚餐,餐饮\n地铁,交通\n公交,交通\n电费,住房';
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'category_import_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Card title="分类管理" extra={
      <Space>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setAddModal(true)}>
          新增分类
        </Button>
        <Button icon={<UploadOutlined />} onClick={() => { setImportModal(true); setImportResult(null); }}>
          批量导入
        </Button>
        <Popconfirm title="确定删除该分类?" onConfirm={handleDelete}
          disabled={!selectedNode}>
          <Button danger icon={<DeleteOutlined />} disabled={!selectedNode}>
            删除选中
          </Button>
        </Popconfirm>
      </Space>
    }>
      {treeData.length > 0 ? (
        <Tree
          treeData={treeData}
          defaultExpandAll
          showLine
          onSelect={(_, info) => {
            setSelectedNode(info.selected ? (info.node as any) : null);
          }}
        />
      ) : (
        <Empty description="暂无分类，请先添加" />
      )}

      <Modal title="新增分类" open={addModal} onOk={() => addForm.submit()}
        onCancel={() => setAddModal(false)} okText="添加" cancelText="取消">
        <Form form={addForm} layout="vertical" onFinish={handleAdd}
          initialValues={{ level: 2 }}>
          <Form.Item name="level" label="分类层级" rules={[{ required: true }]}>
            <Select options={[
              { value: 1, label: '一级分类' },
              { value: 2, label: '二级分类' },
            ]} />
          </Form.Item>
          <Form.Item noStyle shouldUpdate={(prev, cur) => prev.level !== cur.level}>
            {({ getFieldValue }) =>
              getFieldValue('level') === 2 && (
                <Form.Item name="parent_id" label="所属一级分类" rules={[{ required: true, message: '请选择所属一级分类' }]}>
                  <Select placeholder="选择一级分类"
                    options={firstCategories.map((c) => ({ value: c.id, label: c.name }))} />
                </Form.Item>
              )
            }
          </Form.Item>
          <Form.Item name="name" label="分类名称" rules={[{ required: true, message: '请输入分类名称' }]}>
            <Input placeholder="输入分类名称" maxLength={30} />
          </Form.Item>
        </Form>
      </Modal>

      <Modal title="批量导入分类" open={importModal}
        onCancel={() => setImportModal(false)} footer={null}>
        <Upload.Dragger
          accept=".csv"
          showUploadList={false}
          beforeUpload={(file) => { handleImport(file); return false; }}
          disabled={importing}
        >
          <p className="ant-upload-drag-icon"><UploadOutlined style={{ fontSize: 32, color: '#1677ff' }} /></p>
          <p className="ant-upload-text">点击或拖拽 CSV 文件上传</p>
          <p className="ant-upload-hint">
            CSV 格式: 二级分类名称, 一级分类名称<br />
            一级分类不存在时会自动创建
          </p>
        </Upload.Dragger>
        <Button type="link" icon={<DownloadOutlined />} onClick={downloadCategoryTemplate}
          style={{ marginTop: 8, padding: 0 }}>
          下载导入模板
        </Button>

        {importResult && (
          <div style={{ marginTop: 16 }}>
            <p>导入结果: 成功 {importResult.imported} 个分类</p>
            {importResult.errors.length > 0 && (
              <div style={{ maxHeight: 200, overflow: 'auto', background: '#f5f5f5', padding: 12, borderRadius: 6 }}>
                {importResult.errors.map((err, i) => (
                  <p key={i} style={{ color: '#faad14', margin: '4px 0', fontSize: 12 }}>{err}</p>
                ))}
              </div>
            )}
          </div>
        )}
      </Modal>
    </Card>
  );
}
