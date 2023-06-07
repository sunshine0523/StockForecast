const splitDailyData = (stockDailyList) => {
    const rawData = stockDailyList.value
    let categoryData = [];
    let values = [];
    let volumes = [];
    for (let i = 0; i < rawData.length; i++) {
        categoryData.push(rawData[i].trade_date);
        let value = []
        value.push(rawData[i].open)
        value.push(rawData[i].close)
        value.push(rawData[i].low)
        value.push(rawData[i].high)
        value.push(rawData[i].vol)
        values.push(value);
        volumes.push(rawData[i].vol)
    }
    volumes.push('-')
    return {
        categoryData: categoryData,
        values: values,
        volumes: volumes
    };
}

const splitMinuteData = (stockMinuteList) => {
    const rawData = stockMinuteList.value.data
    let times = []
    let values = []
    let volumes = []
    for (let i = 0; i < rawData.length; i++) {
        let splitData = rawData[i].split(' ')
        times.push(splitData[0])
        values.push(splitData[1])
        volumes.push(splitData[2])
    }
    return {
        times: times,
        values: values,
        volumes: volumes
    }
}

// 用于计算均线的函数
function calculateMA(dayCount, data) {
    const result = [];
    for (let i = 0, len = data.values.length; i < len; i++) {
        if (i < dayCount) {
            result.push('-');
            continue;
        }
        let sum = 0;
        for (let j = 0; j < dayCount; j++) {
            sum += data.values[i - j][1];
        }
        result.push(+(sum / dayCount).toFixed(3));
    }
    return result;
}

function getForecast(data, day_count, lastDaysScoreList, forecastClosePrice) {
    let curTime = new Date()
    let today = curTime.getFullYear() + '' + (curTime.getMonth() + 1).toString().padStart(2, '0') + '' + (curTime.getDate()).toString().padStart(2, '0')
    let ma1 = calculateMA(1, data)
    const result = [];
    for (let i = 0, len = data.values.length; i < len - day_count; ++i) {
        result.push('-');
    }
    result.push(ma1[ma1.length - day_count])
    //现在采用的策略，就是后一天的预测价格依赖于前一天的收盘价和这一天的分数
    for (let i = day_count; i > 0; --i) {
        result.push((ma1[ma1.length - i] + lastDaysScoreList.value[day_count - i].score).toFixed(2))
        if (lastDaysScoreList.value[day_count - i].date === today) {

        }
    }
    forecastClosePrice.value = Number(parseFloat(result[result.length - 1]).toFixed(2))
    return result
}

//给分时数据表返回预测数据
function getForecastForMinute(stockMinuteList, forecastClosePrice) {
    let result = []
    let begin = parseFloat(stockMinuteList.value['qt'][5])
    let end = forecastClosePrice.value
    let length = stockMinuteList.value['data'].length
    //240是4h 240min
    let diff = (end - begin) / 240
    for (let i = 0; i <= length - 1; ++i) {
        let value = begin + i * diff
        result.push(value.toFixed(2))
    }
    return result
}

const splitTrendPredictionData = (lastDaysScoreList, stockDailyList) => {
    const forecastRawData = lastDaysScoreList.value
    const dailyRawData = stockDailyList.value
    console.log(dailyRawData)

    let times = []
    let forecast_values = []
    let daily_values = []
    let firstDailyValue = dailyRawData[dailyRawData.length - forecastRawData.length].close
    forecast_values.push(firstDailyValue.toFixed(2))
    daily_values.push(firstDailyValue.toFixed(2))
    times.push('-')
    for (let i = 1; i < forecastRawData.length; i++) {
        //预测值=上一天的预测值+今天的情绪分数
        forecast_values.push((parseFloat(forecast_values[i - 1]) + parseFloat(forecastRawData[i - 1].score)).toFixed(2))
        daily_values.push(dailyRawData[dailyRawData.length - forecastRawData.length + i].close.toFixed(2))
        times.push(forecastRawData[i - 1].date)
    }
    forecast_values.push((parseFloat(forecast_values[forecast_values.length - 1]) + parseFloat(forecastRawData[forecastRawData.length - 1].score)).toFixed(2))
    daily_values.push('-')
    return {
        times: times,
        forecast_values: forecast_values,
        daily_values: daily_values
    }
}

export const updateTrendPredictionEcharts = (trendPredictionChart, lastDaysScoreList, stockDailyList) => {
    const data = splitTrendPredictionData(lastDaysScoreList, stockDailyList)

    // 把配置和数据放这里
    trendPredictionChart.setOption({
        title: [
            {
                left: 'left',
                text: '变化趋势'
            }
        ],
        animation: false,
        legend: {
            left: 'center',
            data: ['预测趋势', '实际趋势']
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            },
            borderWidth: 1,
            borderColor: '#ccc',
            padding: 10,
            textStyle: {
                color: '#000'
            },
            position: function (pos, params, el, elRect, size) {
                const obj = {
                    top: 10
                };
                obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
                return obj;
            }
            // extraCssText: 'width: 170px'
        },
        axisPointer: {
            link: [
                {
                    xAxisIndex: 'all'
                }
            ],
            label: {
                backgroundColor: '#777'
            }
        },
        grid: [
            {
                left: '10%',
                right: '8%',
                height: '70%'
            }
        ],
        xAxis: [
            {
                type: 'category',
                data: data.times,
                boundaryGap: false,
                axisLine: { onZero: false },
                axisTick: { show: true },
                splitLine: { show: false },
                axisLabel: { show: true },
                min: 'dataMin',
                max: 'dataMax',
                axisPointer: {
                    z: 100
                }
            },
        ],
        yAxis: [
            {
                scale: true,
                splitArea: {
                    show: true
                },
                axisLabel: { show: false },
                axisLine: { show: false },
                axisTick: { show: true },
                splitLine: { show: false }
            },
        ],
        series: [
            {
                name: '预测趋势',
                type: 'line',
                data: data.forecast_values,
                lineStyle: {
                    opacity: 1
                }
            },
            {
                name: '实际趋势',
                type: 'line',
                data: data.daily_values,
                lineStyle: {
                    opacity: 1
                }
            },
        ]
    });
}

export const updateStockDailyEcharts = (dailyChart, stockDailyList, forecastDaysCount, lastDaysScoreList, forecastClosePrice) => {
    const data = splitDailyData(stockDailyList)

    // 把配置和数据放这里
    dailyChart.setOption({
        title: [
            {
                left: 'left',
                text: '股票K线图'
            },
            {
                top: '65%',
                left: 'left',
                text: '成交量'
            }
        ],
        animation: false,
        legend: {
            left: 'center',
            data: ['日K', '收盘价', 'MA5', 'MA10', 'MA20', 'MA30', '预计收盘价']
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            },
            borderWidth: 1,
            borderColor: '#ccc',
            padding: 10,
            textStyle: {
                color: '#000'
            },
            position: function (pos, params, el, elRect, size) {
                const obj = {
                    top: 10
                };
                obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
                return obj;
            }
            // extraCssText: 'width: 170px'
        },
        axisPointer: {
            link: [
                {
                    xAxisIndex: 'all'
                }
            ],
            label: {
                backgroundColor: '#777'
            }
        },
        visualMap: {
            show: false,
            seriesIndex: 5,
            dimension: 2,
            pieces: [
                {
                    value: 1,
                    color: '#009f31'
                },
                {
                    value: -1,
                    color: '#ff0000'
                }
            ]
        },
        grid: [
            {
                left: '10%',
                right: '8%',
                height: '50%'
            },
            {
                left: '10%',
                right: '8%',
                top: '63%',
                height: '16%'
            }
        ],
        xAxis: [
            {
                type: 'category',
                data: data.categoryData,
                boundaryGap: false,
                axisLine: { onZero: true },
                axisTick: { show: true },
                splitLine: { show: false },
                axisLabel: { show: false },
                min: 'dataMin',
                max: 'dataMax',
                axisPointer: {
                    z: 100
                }
            },
            {
                type: 'category',
                gridIndex: 1,
                data: data.categoryData,
                boundaryGap: false,
                axisLine: { onZero: true },
                axisTick: { show: true },
                splitLine: { show: false },
                axisLabel: { show: true },
                min: 'dataMin',
                max: 'dataMax'
            }
        ],
        yAxis: [
            {
                scale: true,
                splitArea: {
                    show: true
                }
            },
            {
                scale: true,
                gridIndex: 1,
                splitNumber: 2,
                axisLabel: { show: false },
                axisLine: { show: false },
                axisTick: { show: false },
                splitLine: { show: false }
            }
        ],
        dataZoom: [
            {
                type: 'inside',
                xAxisIndex: [0, 1],
                start: 90,
                end: 100
            },
            {
                show: true,
                xAxisIndex: [0, 1],
                type: 'slider',
                top: '85%',
                start: 0,
                end: 100
            }
        ],
        series: [
            {
                name: '日K',
                type: 'candlestick',
                data: data.values,
                itemStyle: {
                    color: '#ff0000',
                    color0: '#009f31',
                    borderColor: undefined,
                    borderColor0: undefined
                },
            },
            {
                name: '收盘价',
                type: 'line',
                data: calculateMA(1, data),
                smooth: true,
                symbol: "none",
                lineStyle: {
                    opacity: 1
                }
            },
            {
                name: 'MA5',
                type: 'line',
                data: calculateMA(5, data),
                smooth: true,
                symbol: "none",
                lineStyle: {
                    opacity: 1
                }
            },
            {
                name: 'MA10',
                type: 'line',
                data: calculateMA(10, data),
                smooth: true,
                symbol: "none",
                lineStyle: {
                    opacity: 1
                }
            },
            {
                name: 'MA20',
                type: 'line',
                data: calculateMA(10, data),
                smooth: true,
                symbol: "none",
                lineStyle: {
                    opacity: 1
                }
            },
            {
                name: 'MA30',
                type: 'line',
                data: calculateMA(10, data),
                smooth: true,
                symbol: "none",
                lineStyle: {
                    opacity: 1
                }
            },
            {
                name: '预计收盘价',
                type: 'line',
                data: getForecast(data, forecastDaysCount, lastDaysScoreList, forecastClosePrice),
                smooth: true,
                lineStyle: {
                    opacity: 1,
                    type: 'dotted'
                },
            },
            {
                name: '成交量',
                type: 'bar',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: data.volumes
            },
        ]
    });
}

export const updateStockMinuteEcharts = (minuteChart, stockMinuteList, forecastClosePrice) => {
    const data = splitMinuteData(stockMinuteList)

    // 把配置和数据放这里
    minuteChart.setOption({
        title: [
            {
                left: 'left',
                text: '分时图'
            },
            {
                top: '65%',
                left: 'left',
                text: '成交量'
            }
        ],
        animation: false,
        legend: {
            left: 'center',
            data: ['分时', '预测']
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            },
            borderWidth: 1,
            borderColor: '#ccc',
            padding: 10,
            textStyle: {
                color: '#000'
            },
            position: function (pos, params, el, elRect, size) {
                const obj = {
                    top: 10
                };
                obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 30;
                return obj;
            }
            // extraCssText: 'width: 170px'
        },
        axisPointer: {
            link: [
                {
                    xAxisIndex: 'all'
                }
            ],
            label: {
                backgroundColor: '#777'
            }
        },
        grid: [
            {
                left: '10%',
                right: '8%',
                height: '50%'
            },
            {
                left: '10%',
                right: '8%',
                top: '63%',
                height: '16%'
            }
        ],
        xAxis: [
            {
                type: 'category',
                data: data.times,
                boundaryGap: false,
                axisLine: { onZero: true },
                axisTick: { show: true },
                splitLine: { show: false },
                axisLabel: { show: false },
                min: 'dataMin',
                max: 'dataMax',
                axisPointer: {
                    z: 100
                }
            },
            {
                type: 'category',
                gridIndex: 1,
                data: data.times,
                boundaryGap: false,
                axisLine: { onZero: true },
                axisTick: { show: true },
                splitLine: { show: false },
                axisLabel: { show: true },
                min: 'dataMin',
                max: 'dataMax'
            }
        ],
        yAxis: [
            {
                scale: true,
                splitArea: {
                    show: true
                },
            },
            {
                scale: true,
                gridIndex: 1,
                splitNumber: 2,
                axisLabel: { show: false },
                axisLine: { show: false },
                axisTick: { show: false },
                splitLine: { show: false }
            },
        ],
        dataZoom: [
            {
                type: 'inside',
                xAxisIndex: [0, 1],
                start: 0,
                end: 100
            },
            {
                show: true,
                xAxisIndex: [0, 1],
                type: 'slider',
                top: '85%',
                start: 0,
                end: 100
            }
        ],
        series: [
            {
                name: '分时',
                type: 'line',
                data: data.values,
                //基准线
                markLine: {
                    symbol: 'none',
                    data: [
                        {
                            yAxis: stockMinuteList.value['qt'][5],
                            name: "今日开盘价",
                            lineStyle: {
                                // type: "solid",
                                color: "#FA6400",
                                // width: 2,
                            },
                            label: {
                                position: "end",
                                fontSize: 14,
                                formatter: "今日开盘价",
                            },
                        }
                    ]
                }
            },
            {
                name: '预测',
                type: 'line',
                data: getForecastForMinute(stockMinuteList, forecastClosePrice),
                lineStyle: {
                    opacity: 1,
                    type: 'dotted'
                },
            },
            {
                name: '成交量',
                type: 'bar',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: data.volumes
            },
        ]
    });
}