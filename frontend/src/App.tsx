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

const { Sider, Content } = Layout;

const menuItems = [
  { key: '/',           icon: <EditOutlined />,          label: <Link to="/">记账</Link> },
  { key: '/records',    icon: <UnorderedListOutlined />, label: <Link to="/records">账目</Link> },
  { key: '/statistics', icon: <BarChartOutlined />,      label: <Link to="/statistics">统计</Link> },
  { key: '/categories', icon: <TagsOutlined />,          label: <Link to="/categories">分类</Link> },
  { key: '/data',       icon: <DatabaseOutlined />,      label: <Link to="/data">数据</Link> },
];

function Brand() {
  return (
    <Link
      to="/"
      style={{
        height: 64,
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        padding: '0 20px',
        textDecoration: 'none',
      }}
    >
      <span
        style={{
          width: 26,
          height: 26,
          borderRadius: 7,
          background: 'var(--fg)',
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.06)',
        }}
        aria-hidden
      >
        <span
          style={{
            width: 9,
            height: 9,
            borderRadius: 2,
            background: 'var(--accent)',
            transform: 'rotate(45deg)',
          }}
        />
      </span>
      <span
        style={{
          fontWeight: 600,
          fontSize: 15.5,
          letterSpacing: '-0.01em',
          color: 'var(--fg)',
        }}
      >
        Ledger
      </span>
    </Link>
  );
}

function StatusFooter() {
  return (
    <div
      style={{
        position: 'absolute',
        bottom: 16,
        left: 20,
        right: 20,
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '10px 12px',
        borderRadius: 8,
        background: 'var(--surface)',
        border: '1px solid var(--border-soft)',
      }}
    >
      <span className="ledger-status-dot" />
      <span style={{ fontSize: 12, color: 'var(--fg-2)', fontWeight: 500 }}>
        账本已同步
      </span>
      <span
        style={{
          marginLeft: 'auto',
          fontFamily: 'var(--mono)',
          fontSize: 11,
          color: 'var(--fg-3)',
        }}
      >
        v1.0
      </span>
    </div>
  );
}

function AppLayout() {
  const location = useLocation();

  return (
    <Layout style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      <Sider
        breakpoint="lg"
        collapsedWidth="64"
        theme="light"
        width={224}
        style={{
          borderRight: '1px solid var(--border-soft)',
          background: 'var(--bg)',
          position: 'relative',
        }}
      >
        <Brand />
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ paddingTop: 8 }}
        />
        <StatusFooter />
      </Sider>

      <Layout style={{ background: 'var(--bg)' }}>
        <Content className="ledger-content">
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
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#0a0a0a',
          colorInfo: '#0a0a0a',
          colorSuccess: '#16a34a',
          colorError: '#dc2626',
          colorWarning: '#f59e0b',
          colorLink: '#0a0a0a',
          colorLinkHover: '#525252',
          colorBgLayout: '#fafafa',
          colorBgContainer: '#ffffff',
          colorBgElevated: '#ffffff',
          colorBorder: '#e5e5e5',
          colorBorderSecondary: '#f0f0f0',
          colorText: '#0a0a0a',
          colorTextSecondary: '#525252',
          colorTextTertiary: '#a3a3a3',
          colorTextHeading: '#0a0a0a',
          colorTextDescription: '#525252',
          borderRadius: 8,
          borderRadiusLG: 12,
          borderRadiusSM: 6,
          fontFamily:
            "'Geist','Inter',-apple-system,'PingFang SC','Microsoft YaHei','Segoe UI',system-ui,sans-serif",
          fontSize: 14,
          controlHeight: 36,
          wireframe: false,
        },
        components: {
          Layout: {
            siderBg: '#fafafa',
            bodyBg: '#fafafa',
            headerBg: '#fafafa',
          },
          Card: {
            paddingLG: 20,
            boxShadowTertiary: '0 1px 2px rgba(0,0,0,0.04)',
          },
          Button: {
            primaryShadow: 'none',
            defaultShadow: 'none',
            controlHeight: 36,
          },
          Menu: {
            itemBg: 'transparent',
            itemSelectedBg: '#f5f5f5',
            itemSelectedColor: '#0a0a0a',
            itemHoverBg: '#f5f5f5',
            itemHoverColor: '#0a0a0a',
            itemColor: '#525252',
            itemHeight: 36,
            iconSize: 14,
            iconMarginInlineEnd: 10,
            itemMarginInline: 12,
            itemBorderRadius: 8,
            activeBarBorderWidth: 0,
          },
          Table: {
            headerBg: '#fafafa',
            headerColor: '#525252',
            rowHoverBg: '#fafafa',
            headerSplitColor: 'transparent',
            borderColor: '#f0f0f0',
          },
          Tabs: {
            inkBarColor: '#0a0a0a',
            itemSelectedColor: '#0a0a0a',
            itemHoverColor: '#0a0a0a',
            itemActiveColor: '#0a0a0a',
            itemColor: '#525252',
            titleFontSize: 14,
            horizontalItemGutter: 24,
          },
          Tag: {
            defaultBg: '#fafafa',
            defaultColor: '#0a0a0a',
          },
          Modal: {
            borderRadiusLG: 12,
          },
          Form: {
            labelColor: '#525252',
            labelFontSize: 13,
          },
        },
      }}
    >
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </ConfigProvider>
  );
}
