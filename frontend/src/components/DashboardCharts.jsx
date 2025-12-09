import React from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';

export const SkillsChart = ({ data }) => {
    return (
        <div className="card h-96">
            <h3 className="text-xl font-semibold mb-4 text-slate-100">Top Candidate Skills</h3>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={data}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis type="number" stroke="#94a3b8" />
                    <YAxis dataKey="name" type="category" stroke="#94a3b8" width={100} />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '0.5rem' }}
                        itemStyle={{ color: '#f8fafc' }}
                    />
                    <Legend />
                    <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} name="Candidates" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};
