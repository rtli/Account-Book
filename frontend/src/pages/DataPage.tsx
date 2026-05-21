import { useState } from 'react';
import { Card, Upload, Button, message, Divider, Popconfirm, Row, Col, Space } from 'antd';
import { DownloadOutlined, InboxOutlined, DeleteOutlined, WarningOutlined } from '@ant-design/icons';
import { dataApi, categoryApi } from '../services/api';

const { Dragger } = Upload;

function downloadTemplate() {
  const csv = '\uFEFF品名,一级分类,二级分类,金额,日期\n午餐,日常开销,餐饮,35,2025-01-15\n地铁卡充值,日常开销,交通,100,';
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'spending_import_template.csv';
  a.click();
  URL.revokeObjectURL(url);
}

export default function DataPage() {
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<{ imported: number; errors: string[] } | null>(null);

  const [clearing, setClearing] = useState(false);
  const [clearingCategories, setClearingCategories] = useState(false);

  const handleImport = async (file: File) => {
    setImporting(true);
    setImportResult(null);
    try {
      const res = await dataApi.importCsv(file);
      setImportResult(res.data);
      if (res.data.imported > 0) {
        message.success(`成功导入 ${res.data.imported} 条记录`);
      }
      if (res.data.errors.length > 0) {
        message.warning(`有 ${res.data.errors.length} 条记录存在问题`);
      }
    } catch (err: any) {
      message.error(err.response?.data?.detail || '导入失败');
    }
    setImporting(false);
    return false; // prevent default upload
  };

  const handleExport = async () => {
    try {
      const res = await dataApi.exportCsv();
      const blob = new Blob([res.data], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'spending_export.csv';
      a.click();
      URL.revokeObjectURL(url);
      message.success('导出成功');
    } catch {
      message.error('导出失败');
    }
  };

  const handleClear = async () => {
    setClearing(true);
    try {
      const res = await dataApi.clearAll();
      message.success(`已清空 ${res.data.deleted} 条账目记录`);
    } catch {
      message.error('清空失败');
    }
    setClearing(false);
  };

  const handleClearCategories = async () => {
    setClearingCategories(true);
    try {
      const res = await categoryApi.clearAll();
      const parts = [];
      if (res.data.deleted_spendings > 0) parts.push(`${res.data.deleted_spendings} 条账目`);
      if (res.data.deleted_categories > 0) parts.push(`${res.data.deleted_categories} 个分类`);
      message.success(`已清空 ${parts.join('、')}`);
    } catch {
      message.error('清空失败');
    }
    setClearingCategories(false);
  };

  return (
    <div style={{ maxWidth: 800 }}>
      <Row gutter={[16, 16]}>
        {/* ===== 数据导入 ===== */}
        <Col span={24}>
          <Card title="数据导入">
            <Dragger
              accept=".csv"
              showUploadList={false}
              beforeUpload={(file) => { handleImport(file); return false; }}
              disabled={importing}
            >
              <p className="ant-upload-drag-icon"><InboxOutlined /></p>
              <p className="ant-upload-text">点击或拖拽 CSV 文件到此区域上传</p>
              <p className="ant-upload-hint">
                CSV 格式: 品名, 一级分类, 二级分类, 金额, 日期(可选)。分类不存在时自动创建
              </p>
            </Dragger>
            <Button type="link" icon={<DownloadOutlined />} onClick={downloadTemplate}
              style={{ marginTop: 8, padding: 0 }}>
              下载导入模板
            </Button>

            {importResult && (
              <div style={{ marginTop: 16 }}>
                <p>导入结果: 成功 {importResult.imported} 条</p>
                {importResult.errors.length > 0 && (
                  <div style={{ maxHeight: 200, overflow: 'auto', background: '#f5f5f5', padding: 12, borderRadius: 6 }}>
                    {importResult.errors.map((err, i) => (
                      <p key={i} style={{ color: '#faad14', margin: '4px 0', fontSize: 12 }}>{err}</p>
                    ))}
                  </div>
                )}
              </div>
            )}
          </Card>
        </Col>

        {/* ===== 数据导出 ===== */}
        <Col span={24}>
          <Card title="数据导出">
            <p style={{ marginBottom: 16, color: '#666' }}>
              将所有账目记录导出为 CSV 文件，可用于备份或在其他工具中查看。
            </p>
            <Button type="primary" icon={<DownloadOutlined />} onClick={handleExport} size="large">
              导出全部数据
            </Button>
          </Card>
        </Col>

        {/* ===== 危险操作 ===== */}
        <Col span={24}>
          <Card
            title={<span style={{ color: '#ff4d4f' }}><WarningOutlined style={{ marginRight: 8 }} />危险操作</span>}
            styles={{ header: { borderBottom: '1px solid #ffccc7' }, body: { background: '#fff2f0' } }}
          >
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 500 }}>清空全部账目</div>
                  <div style={{ color: '#999', fontSize: 13 }}>删除所有账目记录，分类保留不受影响</div>
                </div>
                <Popconfirm
                  title="确认清空账目"
                  description="此操作将删除所有账目记录且不可恢复，确定要继续吗？"
                  onConfirm={handleClear}
                  okText="确认清空"
                  cancelText="取消"
                  okButtonProps={{ danger: true }}
                >
                  <Button danger icon={<DeleteOutlined />} loading={clearing}>
                    清空账目
                  </Button>
                </Popconfirm>
              </div>
              <Divider style={{ margin: 0 }} />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 500 }}>清空全部分类</div>
                  <div style={{ color: '#999', fontSize: 13 }}>删除所有分类及其关联的账目记录</div>
                </div>
                <Popconfirm
                  title="确认清空分类"
                  description="此操作将删除所有分类以及关联的账目记录且不可恢复，确定要继续吗？"
                  onConfirm={handleClearCategories}
                  okText="确认清空"
                  cancelText="取消"
                  okButtonProps={{ danger: true }}
                >
                  <Button danger icon={<DeleteOutlined />} loading={clearingCategories}>
                    清空分类
                  </Button>
                </Popconfirm>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
