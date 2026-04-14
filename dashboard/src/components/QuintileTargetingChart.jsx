"use client";

import { useMemo } from "react";
import { colors, quintileColors } from "../lib/colors";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import SectionHeading from "./SectionHeading";
import ChartLogo from "./ChartLogo";
import { getQuintileShares } from "../lib/dataHelpers";

const AXIS_STYLE = {
  fontSize: 12,
  fill: colors.gray[500],
};

const QUINTILE_KEYS = ["Q1 (poorest)", "Q2", "Q3", "Q4", "Q5 (richest)"];

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-lg">
      {label !== undefined ? (
        <div className="mb-2 font-semibold text-slate-800">{label}</div>
      ) : null}
      {payload.map((entry) => (
        <div className="flex items-center justify-between gap-4" key={entry.name}>
          <span className="flex items-center gap-2 text-slate-600">
            <span
              className="h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            {entry.name}
          </span>
          <span className="font-medium text-slate-800">
            {entry.value.toFixed(1)}%
          </span>
        </div>
      ))}
    </div>
  );
}

export default function QuintileTargetingChart({ data, scenarioKey }) {
  const quintileData = useMemo(
    () => getQuintileShares(data, scenarioKey),
    [data, scenarioKey],
  );

  if (quintileData.length === 0) return null;

  const chartHeight = Math.max(300, quintileData.length * 60 + 60);

  return (
    <div className="border-t border-slate-200 pt-10">
      <SectionHeading
        title="Policy targeting by income quintile"
        description="Share of each policy's total spending going to each income quintile. Policies that concentrate spending on the poorest quintiles are more progressive."
      />
      <div className="section-card">
        <div style={{ height: chartHeight }} className="w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={quintileData}
              layout="vertical"
              margin={{ left: 10, right: 30, top: 10, bottom: 10 }}
              barSize={24}
            >
              <CartesianGrid strokeDasharray="3 3" stroke={colors.border.light} horizontal={false} />
              <XAxis
                type="number"
                domain={[0, 100]}
                tick={AXIS_STYLE}
                tickLine={false}
                tickFormatter={(v) => `${v}%`}
              />
              <YAxis
                type="category"
                dataKey="policy"
                tick={{ ...AXIS_STYLE, fontSize: 11 }}
                tickLine={false}
                axisLine={false}
                width={180}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: 13 }} />
              {QUINTILE_KEYS.map((key) => (
                <Bar
                  key={key}
                  dataKey={key}
                  name={key}
                  stackId="quintile"
                  fill={quintileColors[key]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
        <ChartLogo />
      </div>
    </div>
  );
}
