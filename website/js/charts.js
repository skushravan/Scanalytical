/**
 * Scanalytical // Chart.js Interactive Visualization Controller
 * Renders dark-themed responsive charts for the true causal drivers of concert turnout & fill rate.
 */

window.ChartEngine = {
  instances: {},

  initAllCharts(summaryData) {
    if (!summaryData) return;
    this.renderArtistTierChart(summaryData.artist_tier_analysis);
    this.renderPriceElasticityChart(summaryData.price_tier_analysis);
    this.renderMarketTierChart(summaryData.market_tier_analysis);
    this.renderGenreChart(summaryData.genre_analysis);
    this.renderTimelineChart(summaryData.timeline_analysis);
    this.renderDayOfWeekChart(summaryData.day_of_week_analysis);
    this.renderMLImportanceChart(summaryData.ml_model ? summaryData.ml_model.factor_importance : {});
  },

  // 1. Artist Fame Tier vs Occupancy & Attendance
  renderArtistTierChart(tierStats) {
    const ctx = document.getElementById('chart-artist-tier');
    if (!ctx || !tierStats) return;

    const labels = tierStats.map(t => t.artist_tier);
    const occupancyVals = tierStats.map(t => t.mean_occupancy);
    const attendanceVals = tierStats.map(t => t.mean_attendance);
    const showsCount = tierStats.map(t => t.shows);

    const palette = [
      'rgba(6, 182, 212, 0.85)',
      'rgba(139, 92, 246, 0.85)',
      'rgba(99, 102, 241, 0.85)',
      'rgba(16, 185, 129, 0.85)',
      'rgba(245, 158, 11, 0.85)',
      'rgba(236, 72, 153, 0.85)'
    ];

    this.instances.artistTier = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Avg Occupancy Rate (%)',
            data: occupancyVals,
            backgroundColor: palette.slice(0, labels.length),
            borderRadius: 6,
            yAxisID: 'y'
          },
          {
            label: 'Avg Attendance',
            data: attendanceVals,
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
            borderColor: 'rgba(255, 255, 255, 0.3)',
            borderWidth: 1.5,
            borderRadius: 6,
            type: 'bar',
            yAxisID: 'y2'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: '#94A3B8', font: { family: 'Inter', size: 12 } }
          },
          tooltip: {
            backgroundColor: '#0F172A',
            borderColor: '#1E293B',
            borderWidth: 1,
            titleColor: '#F8FAFC',
            bodyColor: '#94A3B8',
            callbacks: {
              afterBody: (items) => {
                const idx = items[0].dataIndex;
                return `Concerts Analyzed: ${showsCount[idx]}\nMean Capacity: ${tierStats[idx].mean_capacity.toLocaleString()}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: { color: '#94A3B8', font: { weight: 500 } }
          },
          y: {
            position: 'left',
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: {
              color: '#94A3B8',
              callback: val => `${val}%`
            },
            min: 0,
            max: 105,
            title: { display: true, text: 'Occupancy Rate (%)', color: '#94A3B8' }
          },
          y2: {
            position: 'right',
            grid: { display: false },
            ticks: {
              color: '#64748B',
              callback: val => (val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val)
            },
            title: { display: true, text: 'Avg Attendance', color: '#64748B' }
          }
        }
      }
    });
  },

  // 2. Price Elasticity Chart
  renderPriceElasticityChart(priceStats) {
    const ctx = document.getElementById('chart-price');
    if (!ctx || !priceStats) return;

    const labels = priceStats.map(p => p.price_tier);
    const turnoutVals = priceStats.map(p => p.mean_attendance);
    const occVals = priceStats.map(p => p.mean_occupancy);
    const grossVals = priceStats.map(p => p.total_gross / 1e6);

    this.instances.price = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            type: 'bar',
            label: 'Avg Turnout (Attendees)',
            data: turnoutVals,
            backgroundColor: 'rgba(99, 102, 241, 0.8)',
            borderColor: '#6366F1',
            borderRadius: 6,
            yAxisID: 'y'
          },
          {
            type: 'line',
            label: 'Total Gross ($M)',
            data: grossVals,
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 3,
            pointBackgroundColor: '#10B981',
            pointRadius: 5,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: '#94A3B8', font: { family: 'Inter', size: 12 } }
          },
          tooltip: {
            backgroundColor: '#0F172A',
            borderColor: '#1E293B',
            borderWidth: 1,
            titleColor: '#F8FAFC',
            bodyColor: '#94A3B8',
            callbacks: {
              afterBody: (items) => `Mean Fill Rate: ${occVals[items[0].dataIndex]}%`
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: { color: '#94A3B8' }
          },
          y: {
            position: 'left',
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: {
              color: '#94A3B8',
              callback: val => `${(val / 1000).toFixed(0)}k`
            },
            title: { display: true, text: 'Avg Turnout (Attendees)', color: '#94A3B8' }
          },
          y1: {
            position: 'right',
            grid: { drawOnChartArea: false },
            ticks: {
              color: '#10B981',
              callback: val => `$${val.toFixed(0)}M`
            },
            title: { display: true, text: 'Total Gross ($M)', color: '#10B981' }
          }
        }
      }
    });
  },

  // 3. City Market Tier Chart
  renderMarketTierChart(marketStats) {
    const ctx = document.getElementById('chart-market-tier');
    if (!ctx || !marketStats) return;

    const sorted = [...marketStats].sort((a, b) => b.mean_occupancy - a.mean_occupancy);
    const labels = sorted.map(m =>
      m.market_tier
        .replace(' Global Mega-City', '')
        .replace(' Major Regional Market', '')
        .replace(' Emerging / Secondary Market', ' Secondary')
    );
    const occVals = sorted.map(m => m.mean_occupancy);
    const attVals = sorted.map(m => m.mean_attendance);
    const showsVals = sorted.map(m => m.shows);

    this.instances.marketTier = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Avg Occupancy Rate (%)',
            data: occVals,
            backgroundColor: ['rgba(99, 102, 241, 0.85)', 'rgba(16, 185, 129, 0.85)', 'rgba(245, 158, 11, 0.85)'],
            borderRadius: 8
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0F172A',
            borderColor: '#1E293B',
            borderWidth: 1,
            titleColor: '#F8FAFC',
            bodyColor: '#94A3B8',
            callbacks: {
              title: (items) => sorted[items[0].dataIndex].market_tier,
              label: (ctx) => `Avg Occupancy: ${ctx.raw.toFixed(1)}%`,
              afterLabel: (ctx) => `Avg Attendance: ${Math.round(attVals[ctx.dataIndex]).toLocaleString()} fans\nConcerts Analyzed: ${showsVals[ctx.dataIndex]}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: { color: '#F8FAFC', font: { weight: 600 } }
          },
          y: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: {
              color: '#94A3B8',
              callback: val => `${val}%`
            },
            min: 60,
            max: 100,
            title: { display: true, text: 'Occupancy Rate (%)', color: '#94A3B8' }
          }
        }
      }
    });
  },

  // 4. Musical Genre Chart
  renderGenreChart(genreStats) {
    const ctx = document.getElementById('chart-genre');
    if (!ctx || !genreStats) return;

    // Filter to genres with at least 15 shows
    const valid = [...genreStats].filter(g => g.shows >= 15).sort((a, b) => b.mean_occupancy - a.mean_occupancy);

    this.instances.genre = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: valid.map(g => g.genre),
        datasets: [
          {
            label: 'Avg Occupancy Rate (%)',
            data: valid.map(g => g.mean_occupancy),
            backgroundColor: 'rgba(16, 185, 129, 0.85)',
            borderRadius: 6
          }
        ]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0F172A',
            borderColor: '#1E293B',
            borderWidth: 1,
            titleColor: '#F8FAFC',
            bodyColor: '#94A3B8',
            callbacks: {
              label: (ctx) => `Avg Fill Rate: ${ctx.raw.toFixed(1)}%`,
              afterLabel: (ctx) => `Avg Turnout: ${Math.round(valid[ctx.dataIndex].mean_attendance).toLocaleString()} fans\nShows: ${valid[ctx.dataIndex].shows}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: { color: '#94A3B8', callback: val => `${val}%` },
            min: 50,
            max: 100
          },
          y: {
            grid: { display: false },
            ticks: { color: '#F8FAFC', font: { weight: 600 }, autoSkip: false }
          }
        }
      }
    });
  },

  // 5. Timeline & Economic Trend Chart
  renderTimelineChart(timelineStats) {
    const ctx = document.getElementById('chart-timeline');
    if (!ctx || !timelineStats) return;

    const filtered = timelineStats.filter(y => y.year >= 2009);

    this.instances.timeline = new Chart(ctx, {
      type: 'line',
      data: {
        labels: filtered.map(y => String(y.year)),
        datasets: [
          {
            label: 'Avg Turnout per Show',
            data: filtered.map(y => y.mean_attendance),
            borderColor: '#6366F1',
            backgroundColor: 'rgba(99, 102, 241, 0.12)',
            fill: true,
            tension: 0.35,
            pointBackgroundColor: filtered.map(y => (y.year === 2020 || y.year === 2021 ? '#EF4444' : '#6366F1')),
            pointBorderColor: '#FFFFFF',
            pointRadius: 6,
            pointHoverRadius: 9
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0F172A',
            borderColor: '#1E293B',
            borderWidth: 1,
            titleColor: '#F8FAFC',
            bodyColor: '#94A3B8',
            callbacks: {
              label: (ctx) => `Avg Turnout: ${Math.round(ctx.raw).toLocaleString()} attendees`,
              afterLabel: (ctx) => (ctx.label === '2020' || ctx.label === '2021' ? '⚠ COVID-19 pandemic restriction era' : '')
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: { color: '#94A3B8' }
          },
          y: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: {
              color: '#94A3B8',
              callback: val => `${(val / 1000).toFixed(0)}k`
            },
            title: { display: true, text: 'Attendees per Show', color: '#94A3B8' }
          }
        }
      }
    });
  },

  // 6. Day of Week Chart
  renderDayOfWeekChart(dayStats) {
    const ctx = document.getElementById('chart-dayofweek');
    if (!ctx || !dayStats) return;

    const labels = dayStats.map(d => d.day_of_week);
    const turnoutVals = dayStats.map(d => d.mean_attendance);
    const occVals = dayStats.map(d => d.mean_occupancy);
    const showsVals = dayStats.map(d => d.shows);

    this.instances.dayofweek = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Avg Turnout (Attendees)',
            data: turnoutVals,
            backgroundColor: labels.map(d => (['Friday', 'Saturday', 'Sunday'].includes(d) ? 'rgba(99, 102, 241, 0.85)' : 'rgba(139, 92, 246, 0.5)')),
            borderColor: '#6366F1',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0F172A',
            borderColor: '#1E293B',
            borderWidth: 1,
            callbacks: {
              label: (ctx) => `Turnout: ${Math.round(ctx.raw).toLocaleString()} attendees`,
              afterLabel: (ctx) => `Fill Rate: ${occVals[ctx.dataIndex]}%\nShows Scheduled: ${showsVals[ctx.dataIndex]}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: { color: '#94A3B8' }
          },
          y: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: {
              color: '#94A3B8',
              callback: val => `${(val / 1000).toFixed(0)}k`
            }
          }
        }
      }
    });
  },

  // 7. ML Feature Importance Chart
  renderMLImportanceChart(factorImportance) {
    const ctx = document.getElementById('chart-ml-importance');
    if (!ctx || !factorImportance) return;

    const sortedEntries = Object.entries(factorImportance).sort((a, b) => b[1] - a[1]);
    const labels = sortedEntries.map(e => e[0]);
    const values = sortedEntries.map(e => e[1]);

    this.instances.ml = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Predictive Influence (%)',
            data: values,
            backgroundColor: 'rgba(99, 102, 241, 0.85)',
            borderColor: '#6366F1',
            borderRadius: 6
          }
        ]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#0F172A',
            borderColor: '#1E293B',
            callbacks: {
              label: (ctx) => ` Relative Importance: ${ctx.parsed.x.toFixed(2)}%`
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(30, 41, 59, 0.4)' },
            ticks: { color: '#94A3B8', callback: val => `${val}%` }
          },
          y: {
            grid: { display: false },
            ticks: { color: '#F8FAFC', font: { size: 11 } }
          }
        }
      }
    });
  }
};
