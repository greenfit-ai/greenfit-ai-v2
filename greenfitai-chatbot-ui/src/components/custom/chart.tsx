import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

const EvaluationChart = ({ data }: { data: number[] }) => {
  const chartData = [
    { name: 'Carbon', value: data[0] },
    { name: 'Water', value: data[1] },
    { name: 'Energy', value: data[2] }
  ];

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Average evaluation score</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Bar dataKey="value" fill="#33cc33" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};

export default EvaluationChart;