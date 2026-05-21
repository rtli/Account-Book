import { useState, useEffect } from 'react';
import { Card, Select, DatePicker, Space, Empty, Row, Col } from 'antd';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';
import { statisticsApi, type SankeyData, type MonthlySummary, type CategorySummary } from '../services/api';

export default function StatisticsPage() {
  const [year, setYear] = useState<number>(dayjs().year());
  const [month, setMonth] = useState<number | undefined>(undefined);
  const [sankeyData, setSankeyData] = useState<SankeyData>({ nodes: [], links: [] });
  const [monthlyData, setMonthlyData] = useState<MonthlySummary[]>([]);
  const [categoryData, setCategoryData] = useState<CategorySummary[]>([]);

  useEffect(() => {
    statisticsApi.sankey({ year, month }).then((res) => setSankeyData(res.data));
    statisticsApi.categorySummary({ year, month }).then((res) => setCategoryData(res.data));
  }, [year, month]);

  useEffect(() => {
    statisticsApi.monthly({ year }).then((res) => setMonthlyData(res.data));
  }, [year]);

  const sankeyOption = {
    tooltip: { trigger: 'item', triggerOn: 'mousemove' },
    series: [{
      type: 'sankey',
      data: sankeyData.nodes,
      links: sankeyData.links,
      emphasis: { focus: 'adjacency' },
      lineStyle: { color: 'gradient', curveness: 0.5 },
      label: { fontSize: 12 },
    }],
  };

  const barOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: monthlyData.map((m) => m.month) },
    yAxis: { type: 'value', name: '金额 (元)' },
    series: [{
      type: 'bar',
      data: monthlyData.map((m) => m.total),
      itemStyle: { color: '#1677ff' },
    }],
  };

  const pieOption = {
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'middle' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: true,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}\n¥{c}' },
      data: categoryData.map((c) => ({ name: c.name, value: c.total })),
    }],
  };

  const months = Array.from({ length: 12 }, (_, i) => ({ value: i + 1, label: `${i + 1}月` }));

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <DatePicker picker="year" value={dayjs().year(year)} onChange={(d) => d && setYear(d.year())} />
        <Select placeholder="全部月份" allowClear style={{ width: 100 }}
          options={months} value={month} onChange={setMonth} />
      </Space>

      <Card title="资金流向 (桑基图)" style={{ marginBottom: 24 }}>
        {sankeyData.nodes.length > 0 ? (
          <ReactECharts option={sankeyOption} style={{ height: 500 }} />
        ) : (
          <Empty description="暂无数据" />
        )}
      </Card>

      <Row gutter={24}>
        <Col xs={24} lg={14}>
          <Card title="月度支出趋势">
            {monthlyData.length > 0 ? (
              <ReactECharts option={barOption} style={{ height: 350 }} />
            ) : (
              <Empty description="暂无数据" />
            )}
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="分类支出占比">
            {categoryData.length > 0 ? (
              <ReactECharts option={pieOption} style={{ height: 350 }} />
            ) : (
              <Empty description="暂无数据" />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}
