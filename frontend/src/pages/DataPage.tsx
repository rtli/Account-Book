import { useState } from 'react';
import { Card, Upload, Button, message, Space, Divider } from 'antd';
import { UploadOutlined, DownloadOutlined, InboxOutlined } from '@ant-design/icons';
import { dataApi } from '../services/api';

const { Dragger } = Upload;

function downloadTemplate() {
  const csv = '\uFEFF品名,分类名称,金额,日期\n午餐,餐饮,35,2025-01-15\n地铁卡充值,交通,100,';
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

  return (
    <div style={{ maxWidth: 700 }}>
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
            CSV 格式: 品名, 分类名称, 金额, 日期(可选, YYYY-MM-DD)
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

      <Divider />

      <Card title="数据导出">
        <p style={{ marginBottom: 16, color: '#666' }}>
          将所有账目记录导出为 CSV 文件，可用于备份或在其他工具中查看。
        </p>
        <Button type="primary" icon={<DownloadOutlined />} onClick={handleExport} size="large">
          导出全部数据
        </Button>
      </Card>
    </div>
  );
}
