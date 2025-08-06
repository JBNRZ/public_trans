import {useEffect, useRef} from "react";
import * as echarts from 'echarts/core';
import {GraphChart} from 'echarts/charts';
import {SVGRenderer} from 'echarts/renderers';
import {TooltipComponent} from 'echarts/components';
import './App.css'


function App() {
  const chartRef = useRef(null);
  let nodes = [];
  for (let i = 0; i < 10; i++) {
    nodes.push({fixed: false, symbolSize: 30, id: i, name: 'test '+i});
  }

  useEffect(() => {
    echarts.use([GraphChart, SVGRenderer, TooltipComponent]);
    const myChart = echarts.init(chartRef.current);
    let option;

    option = {
      tooltip: {
        trigger: 'item',
        formatter: function (value) {
          if (value.dataType === 'node') {
            return value.data.name;
          } else if (value.dataType === 'edge') {
            return value.data.source + ' -> ' + value.data.target;
          } else {
            return 'unknown';
          }
        }
      },
      series: [
        {
          type: 'graph',
          layout: 'force',
          animation: true,
          animationEasing: 'quinticOut',
          animationDuration: 500,
          nodes: nodes,
          edgeSymbol: ['circle', 'arrow'],
          edgeSymbolSize: [4, 10],
          edgeLabel: {
            fontSize: 20
          },
          roam: true,
          draggable: true,
          label: {
            show: true,
            position: 'bottom',
            formatter: '{b}',
          },
          labelLayout: {
            hideOverlap: true
          },
          lineStyle: {
            color: 'source',
            curveness: 0.2
          },
        }
      ]
    };
    setInterval(function () {
      let edges = []
      for (let i = 0; i < 10; i++) {
        const source = Math.round((nodes.length - 1) * Math.random());
        const target = Math.round((nodes.length - 1) * Math.random());
        edges.push({
          source: source,
          target: target
        });
        edges.push({
          source: target,
          target: source,
        })
      }
      myChart.setOption({
        series: [
          {
            edges: edges
          }
        ]
      });
    }, 10000);

    option && myChart.setOption(option);

  })

  return (
    <>
      <div className="text-center">
        <h2>React Echarts 折线+柱状图</h2>
      </div>
      <div>
        <div ref={chartRef} style={{ height: '700px' }}></div>
      </div>
    </>
  )
}

export default App
