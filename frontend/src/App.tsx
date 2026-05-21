import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Layout, Menu, ConfigProvider, theme } from 'antd';
import {
  EditOutlined,
  UnorderedListOutlined,
  BarChartOutlined,
  TagsOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import zhCN from 'antd/locale/zh_CN';

import HomePage from './pages/HomePage';
import RecordsPage from './pages/RecordsPage';
import StatisticsPage from './pages/StatisticsPage';
import CategoriesPage from './pages/CategoriesPage';
import DataPage from './pages/DataPage';

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: '/', icon: <EditOutlined />, label: <Link to="/">记账</Link> },
  { key: '/records', icon: <UnorderedListOutlined />, label: <Link to="/records">账目</Link> },
  { key: '/statistics', icon: <BarChartOutlined />, label: <Link to="/statistics">统计</Link> },
  { key: '/categories', icon: <TagsOutlined />, label: <Link to="/categories">分类</Link> },
  { key: '/data', icon: <DatabaseOutlined />, label: <Link to="/data">数据</Link> },
];

function AppLayout() {
  const location = useLocation();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="60" theme="light"
        style={{ borderRight: '1px solid #f0f0f0' }}>
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 18, color: '#1677ff' }}>
          Account Book
        </div>
        <Menu mode="inline" selectedKeys={[location.pathname]} items={menuItems} />
      </Sider>
      <Layout>
        <Content style={{ margin: 24, padding: 24, background: '#fff', borderRadius: 8, overflow: 'auto' }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/records" element={<RecordsPage />} />
            <Route path="/statistics" element={<StatisticsPage />} />
            <Route path="/categories" element={<CategoriesPage />} />
            <Route path="/data" element={<DataPage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default function App() {
  return (
    <ConfigProvider locale={zhCN} theme={{ algorithm: theme.defaultAlgorithm }}>
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </ConfigProvider>
  );
}
