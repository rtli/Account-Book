import { useState, useEffect, useCallback, useMemo } from 'react';
import { Card, Select, DatePicker, Space, Empty, Spin, Tabs, Button, Typography, message } from 'antd';
import { ZoomInOutlined, ZoomOutOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  statisticsApi,
  categoryApi,
  type SankeyData,
  type MonthlySummary,
  type CategorySummary,
  type Category,
} from '../services/api';

const { Text } = Typography;

// ========== Layout Constants ==========
const BASE_NODE_GAP = 18;
const DRILLDOWN_GAP_MULTIPLIER = 2;
const MIN_CHART_HEIGHT_FULL = 500;
const MIN_CHART_HEIGHT_DRILLDOWN = 300;
const NODE_SPACING_FULL = 16;
const NODE_SPACING_DRILLDOWN = 20;
const VIEWPORT_HEIGHT = 600;
const ZOOM_STEP = 0.25;
const ZOOM_MIN = 0.5;
const ZOOM_MAX = 3;

const MONTH_OPTIONS = Array.from({ length: 12 }, (_, i) => ({ value: i + 1, label: `${i + 1}月` }));

export default function StatisticsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const incomingState = location.state as { year?: number; month?: number; parent?: string | null } | null;
  const [year, setYear] = useState<number>(incomingState?.year ?? dayjs().year());
  const [month, setMonth] = useState<number | undefined>(incomingState?.month ?? undefined);
  const [sankeyData, setSankeyData] = useState<SankeyData>({ nodes: [], links: [] });
  const [monthlyData, setMonthlyData] = useState<MonthlySummary[]>([]);
  const [categoryData, setCategoryData] = useState<CategorySummary[]>([]);
  const [subCategories, setSubCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState({ sankey: false, monthly: false, category: false });
  const [sankeyZoom, setSankeyZoom] = useState(1);
  const [selectedParent, setSelectedParent] = useState<string | null>(null);
  // Pending parent to restore after sankey data is loaded (when returning from records page)
  const [pendingParent, setPendingParent] = useState<string | null>(incomingState?.parent ?? null);

  // Clear navigation state once consumed so a manual refresh won't re-apply it
  useEffect(() => {
    if (incomingState) {
      navigate(location.pathname, { replace: true, state: null });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    categoryApi.list()
      .then((res) => setSubCategories(res.data.filter((c) => c.level === 2)))
      .catch(() => { /* ignore */ });
  }, []);

  const fetchSankeyAndCategory = useCallback(async () => {
    setSelectedParent(null);
    setSankeyZoom(1);
    setLoading((prev) => ({ ...prev, sankey: true, category: true }));
    try {
      const [sankeyRes, categoryRes] = await Promise.all([
        statisticsApi.sankey({ year, month }),
        statisticsApi.categorySummary({ year, month }),
      ]);
      setSankeyData(sankeyRes.data);
      setCategoryData(categoryRes.data);
    } catch {
      message.error('加载统计数据失败');
    } finally {
      setLoading((prev) => ({ ...prev, sankey: false, category: false }));
    }
  }, [year, month]);

  const fetchMonthly = useCallback(async () => {
    setLoading((prev) => ({ ...prev, monthly: true }));
    try {
      const res = await statisticsApi.monthly({ year });
      setMonthlyData(res.data);
    } catch {
      message.error('加载月度数据失败');
    } finally {
      setLoading((prev) => ({ ...prev, monthly: false }));
    }
  }, [year]);

  useEffect(() => { fetchSankeyAndCategory(); }, [fetchSankeyAndCategory]);
  useEffect(() => { fetchMonthly(); }, [fetchMonthly]);

  // Identify first-level category nodes: appear as both source and target in links
  const parentCategorySet = useMemo(() => {
    const sourceSet = new Set(sankeyData.links.map((l) => l.source));
    const targetSet = new Set(sankeyData.links.map((l) => l.target));
    return new Set(
      sankeyData.nodes
        .filter((n) => sourceSet.has(n.name) && targetSet.has(n.name))
        .map((n) => n.name)
    );
  }, [sankeyData]);

  // Restore drill-down state once sankey data has loaded the matching parent
  useEffect(() => {
    if (pendingParent && parentCategorySet.has(pendingParent)) {
      setSelectedParent(pendingParent);
      setPendingParent(null);
    }
  }, [pendingParent, parentCategorySet]);

  // Identify second-level category nodes: appear only as source (leftmost leaves)
  const subCategorySet = useMemo(() => {
    const sourceSet = new Set(sankeyData.links.map((l) => l.source));
    const targetSet = new Set(sankeyData.links.map((l) => l.target));
    return new Set(
      sankeyData.nodes
        .filter((n) => sourceSet.has(n.name) && !targetSet.has(n.name))
        .map((n) => n.name)
    );
  }, [sankeyData]);

  // Compute date range from current year/month filter for drilling into records
  const getDateRange = useCallback(() => {
    if (month != null) {
      const start = dayjs(`${year}-${String(month).padStart(2, '0')}-01`);
      return { start: start.format('YYYY-MM-DD'), end: start.endOf('month').format('YYYY-MM-DD') };
    }
    return { start: `${year}-01-01`, end: `${year}-12-31` };
  }, [year, month]);

  // Filtered view when a parent category is selected
  const displaySankeyData = useMemo((): SankeyData => {
    if (!selectedParent) return sankeyData;
    const filteredLinks = sankeyData.links.filter(
      (l) => l.target === selectedParent || l.source === selectedParent
    );
    const nodeNames = new Set(filteredLinks.flatMap((l) => [l.source, l.target]));
    return {
      nodes: sankeyData.nodes.filter((n) => nodeNames.has(n.name)),
      links: filteredLinks,
    };
  }, [sankeyData, selectedParent]);

  // Count left-side nodes (sub-categories) to determine chart height
  const subCategoryCount = useMemo(() => {
    const targetSet = new Set(displaySankeyData.links.map((l) => l.target));
    return displaySankeyData.nodes.filter((n) => !targetSet.has(n.name)).length;
  }, [displaySankeyData]);
  const nodeGap = selectedParent ? BASE_NODE_GAP * DRILLDOWN_GAP_MULTIPLIER * sankeyZoom : BASE_NODE_GAP * sankeyZoom;
  const sankeyChartHeight = selectedParent
    ? Math.max(MIN_CHART_HEIGHT_DRILLDOWN, subCategoryCount * (nodeGap + NODE_SPACING_DRILLDOWN))
    : Math.max(MIN_CHART_HEIGHT_FULL, subCategoryCount * (nodeGap + NODE_SPACING_FULL));
  const sankeyViewportHeight = VIEWPORT_HEIGHT;

  const sankeyOption = useMemo(() => ({
    tooltip: {
      trigger: 'item' as const,
      triggerOn: 'mousemove' as const,
      formatter: (params: { dataType: string; name: string; value?: number; data?: { source: string; target: string; value: number } }) => {
        if (params.dataType === 'node') {
          const val = params.value != null ? `¥${params.value.toFixed(2)}` : '';
          let hint = '';
          if (parentCategorySet.has(params.name) && !selectedParent) {
            hint = '<br/><span style="color:#1677ff;font-size:11px">点击查看明细</span>';
          } else if (subCategorySet.has(params.name)) {
            hint = '<br/><span style="color:#1677ff;font-size:11px">点击查看账目</span>';
          }
          return `<strong>${params.name}</strong> ${val}${hint}`;
        }
        if (params.data) {
          return `${params.data.source} → ${params.data.target}<br/>¥${params.data.value.toFixed(2)}`;
        }
        return '';
      },
    },
    series: [{
      type: 'sankey',
      data: displaySankeyData.nodes,
      links: displaySankeyData.links,
      emphasis: { focus: 'adjacency' },
      lineStyle: { color: 'gradient', curveness: 0.5 },
      label: { fontSize: selectedParent ? 14 : 13, color: '#333' },
      nodeWidth: 24,
      nodeGap,
      layoutIterations: 32,
      left: 10,
      right: 60,
      top: 10,
      bottom: 10,
    }],
  }), [displaySankeyData, nodeGap, selectedParent, parentCategorySet, subCategorySet]);

  const onSankeyEvents = useMemo(() => ({
    click: (params: { dataType: string; name: string }) => {
      if (params.dataType !== 'node') return;
      // Sub-category click: jump to records page filtered by category + date range
      if (subCategorySet.has(params.name)) {
        const cat = subCategories.find((c) => c.name === params.name);
        if (!cat) {
          message.warning('未找到该分类，可能数据未同步');
          return;
        }
        const { start, end } = getDateRange();
        const qs = new URLSearchParams({
          category_id: String(cat.id),
          start_date: start,
          end_date: end,
        });
        navigate(`/records?${qs.toString()}`, {
          state: { from: 'statistics', year, month, parent: selectedParent },
        });
        return;
      }
      // Parent-category click in full view: drill down within sankey
      if (parentCategorySet.has(params.name) && !selectedParent) {
        setSelectedParent(params.name);
        setSankeyZoom(1);
      }
    },
  }), [parentCategorySet, subCategorySet, selectedParent, subCategories, getDateRange, navigate, year, month]);

  const barOption = {
    tooltip: { trigger: 'axis', formatter: '{b}<br/>支出: ¥{c}' },
    grid: { left: 60, right: 20, bottom: 40, top: 30 },
    xAxis: {
      type: 'category',
      data: monthlyData.map((m) => m.month),
      axisLabel: { rotate: monthlyData.length > 6 ? 30 : 0 },
    },
    yAxis: { type: 'value', name: '金额 (元)' },
    series: [{
      type: 'bar',
      data: monthlyData.map((m) => m.total),
      itemStyle: { color: '#1677ff', borderRadius: [4, 4, 0, 0] },
      barMaxWidth: 40,
    }],
  };

  const pieOption = {
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      textStyle: { fontSize: 13 },
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['60%', '50%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: {
        show: true,
        formatter: (params: { name: string; value: number; percent: number }) =>
          `${params.name}\n¥${params.value} (${params.percent}%)`,
        fontSize: 12,
      },
      data: categoryData.map((c) => ({ name: c.name, value: c.total })),
    }],
  };

  const months = MONTH_OPTIONS;

  const tabItems = [
    {
      key: 'sankey',
      label: '资金流向',
      children: (
        <Spin spinning={loading.sankey}>
          {sankeyData.nodes.length > 0 ? (
            <div>
              <Space style={{ marginBottom: 8 }} align="center">
                {selectedParent ? (
                  <>
                    <Button icon={<ArrowLeftOutlined />} size="small"
                      onClick={() => { setSelectedParent(null); setSankeyZoom(1); }}>
                      返回全览
                    </Button>
                    <Text strong style={{ fontSize: 14 }}>{selectedParent}</Text>
                    <Text type="secondary" style={{ fontSize: 12 }}>— {subCategoryCount} 个二级分类</Text>
                  </>
                ) : (
                  <Text type="secondary" style={{ fontSize: 12 }}>点击一级分类查看明细，点击二级分类查看账目</Text>
                )}
                <Button icon={<ZoomInOutlined />} size="small"
                  onClick={() => setSankeyZoom((z) => Math.min(z + ZOOM_STEP, ZOOM_MAX))} />
                <Button icon={<ZoomOutOutlined />} size="small"
                  onClick={() => setSankeyZoom((z) => Math.max(z - ZOOM_STEP, ZOOM_MIN))} />
                <span style={{ fontSize: 12, color: '#999' }}>{Math.round(sankeyZoom * 100)}%</span>
              </Space>
              <div style={{ height: sankeyViewportHeight, overflowY: 'auto', border: '1px solid #f0f0f0', borderRadius: 8 }}>
                <ReactECharts
                  option={sankeyOption}
                  style={{ height: sankeyChartHeight }}
                  onEvents={onSankeyEvents}
                />
              </div>
            </div>
          ) : (
            <Empty description="暂无数据" style={{ padding: 60 }} />
          )}
        </Spin>
      ),
    },
    {
      key: 'monthly',
      label: '月度趋势',
      children: (
        <Spin spinning={loading.monthly}>
          {monthlyData.length > 0 ? (
            <ReactECharts option={barOption} style={{ height: 500 }} />
          ) : (
            <Empty description="暂无数据" style={{ padding: 60 }} />
          )}
        </Spin>
      ),
    },
    {
      key: 'category',
      label: '分类占比',
      children: (
        <Spin spinning={loading.category}>
          {categoryData.length > 0 ? (
            <ReactECharts option={pieOption} style={{ height: 500 }} />
          ) : (
            <Empty description="暂无数据" style={{ padding: 60 }} />
          )}
        </Spin>
      ),
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <DatePicker picker="year" value={dayjs().year(year)} onChange={(d) => d && setYear(d.year())} />
        <Select placeholder="全部月份" allowClear style={{ width: 100 }}
          options={months} value={month} onChange={setMonth} />
      </Space>

      <Card>
        <Tabs items={tabItems} size="large" />
      </Card>
    </div>
  );
}
