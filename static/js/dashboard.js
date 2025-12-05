// Enhanced Airport Dashboard with AI-Powered Conveyor Belt System
class AirportDashboard {
    constructor(airportCode) {
        this.airportCode = airportCode;
        this.refreshInterval = 90000; // 90 seconds (1.5 minutes) for real-time updates
        this.conveyorData = null;
        this.aiAlerts = [];
        const config = window.dashboardConfig || {};
        this.alertScopes = Array.isArray(config.alertScopes) && config.alertScopes.length
            ? config.alertScopes
            : ['all'];
        this.beltStages = [
            {
                id: 'checking',
                label: 'Check-In & Tagging',
                description: 'Bags dropped and tagged',
                icon: 'fas fa-clipboard-check',
                start: 0,
                end: 25
            },
            {
                id: 'sorting',
                label: 'Automated Sorting',
                description: 'Intelligent diverters align bags',
                icon: 'fas fa-diagram-project',
                start: 25,
                end: 50
            },
            {
                id: 'security',
                label: 'Security Screening',
                description: 'Explosive trace & X-ray scanning',
                icon: 'fas fa-shield-halved',
                start: 50,
                end: 75
            },
            {
                id: 'boarding',
                label: 'Gate Boarding',
                description: 'Loaded on dollies and trolleys',
                icon: 'fas fa-plane-departure',
                start: 75,
                end: 100
            }
        ];
        this.datasetEndpoints = {
            passenger_flow: 'passenger-flow',
            queue_status: 'queue-status',
            baggage_tracking: 'baggage-tracking',
            flight_status: 'flight-status',
            security_status: 'security-status',
            resource_utilization: 'resource-utilization',
            staff_availability: 'staff-availability'
        };
        this.init();
    }

    getBeltStages() {
        return this.beltStages || [];
    }

    generateStageOverlayHTML(belt) {
        const stages = this.getBeltStages();
        if (!stages.length) return '';

        const counts = this.calculateStageCounts(belt);

        return `
            <div class="belt-stage-overlay">
                ${stages.map(stage => `
                    <div class="belt-stage-segment belt-stage-${stage.id}" style="width: ${stage.end - stage.start}%;">
                        <div class="stage-label">
                            <span>${stage.label}</span>
                            <small>${counts[stage.id] || 0} bags</small>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    generateStageTimelineHTML(belt) {
        const stages = this.getBeltStages();
        if (!stages.length) return '';

        const counts = this.calculateStageCounts(belt);
        const bagCount = belt && Array.isArray(belt.bags_on_belt) ? belt.bags_on_belt.length : 0;
        const totalBags = Math.max(1, bagCount);
        const dominantStage = this.getDominantStage(counts);

        return `
            <div class="belt-stage-flow">
                ${stages.map((stage, index) => {
                    const loadPercent = Math.round((counts[stage.id] || 0) / totalBags * 100);
                    const flowState = this.getStageFlowState(loadPercent, counts[stage.id]);
                    const isActive = dominantStage === stage.id ? 'active' : '';

                    return `
                        <div class="flow-stage flow-stage-${stage.id} ${isActive}">
                            <div class="flow-stage-header">
                                <span class="flow-stage-icon"><i class="${stage.icon}"></i></span>
                                <div>
                                    <strong>${stage.label}</strong>
                                    <small>${stage.description}</small>
                                </div>
                            </div>
                            <div class="flow-stage-progress">
                                <div class="flow-stage-progress-fill" style="width: ${loadPercent}%;"></div>
                            </div>
                            <div class="flow-stage-meta">
                                <span>${counts[stage.id] || 0} bags</span>
                                <span>${flowState}</span>
                            </div>
                        </div>
                        ${index < stages.length - 1 ? '<div class="flow-connector"><span class="flow-dot"></span></div>' : ''}
                    `;
                }).join('')}
            </div>
        `;
    }

    calculateStageCounts(belt) {
        const stages = this.getBeltStages();
        const counts = stages.reduce((acc, stage) => {
            acc[stage.id] = 0;
            return acc;
        }, {});

        if (!belt || !Array.isArray(belt.bags_on_belt)) {
            return counts;
        }

        belt.bags_on_belt.forEach(bag => {
            const stageId = this.getStageForPosition(bag.position);
            if (stageId && typeof counts[stageId] === 'number') {
                counts[stageId] += 1;
            }
        });

        return counts;
    }

    getStageForPosition(position) {
        const stages = this.getBeltStages();
        if (!stages.length) return null;

        const stage = stages.find(stage => position >= stage.start && position < stage.end);
        return stage ? stage.id : stages[stages.length - 1].id;
    }

    getStageFlowState(loadPercent, count) {
        if (count === 0) return 'Idle';
        if (loadPercent >= 60) return 'Congested';
        if (loadPercent >= 30) return 'Flowing';
        return 'Clearing';
    }

    getDominantStage(counts) {
        const entries = Object.entries(counts || {});
        if (!entries.length) return null;

        let dominantStage = entries[0][0];
        let maxCount = entries[0][1];

        entries.forEach(([stageId, count]) => {
            if (count > maxCount) {
                dominantStage = stageId;
                maxCount = count;
            }
        });

        return dominantStage;
    }

    init() {
        this.loadAllData();
        this.setupAutoRefresh();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Theme toggle
        const themeToggle = document.querySelector('[onclick="toggleTheme()"]');
        if (themeToggle) {
            themeToggle.addEventListener('click', this.toggleTheme.bind(this));
        }
    }

    async loadAllData() {
        try {
            this.showLoading(true);
            
            // Load all dashboard data including conveyor system
            const response = await fetch(`/api/airport/${this.airportCode}/dashboard-data`);
            let data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            data = await this.handleDatasetRecovery(data);
            
            // Load conveyor system data separately for enhanced features
            const conveyorResponse = await fetch(`/api/airport/${this.airportCode}/live-conveyors`);
            const conveyorData = await conveyorResponse.json();
            
            if (!conveyorData.error) {
                this.conveyorData = conveyorData;
                this.renderConveyorSystem();
                this.renderAIAlerts();
                this.renderAIInsights();
            }

            // Render all other widgets
            this.renderPassengerFlow(data.passenger_flow);
            this.renderQueueStatus(data.queue_status);
            this.renderBaggageTracking(data.baggage_tracking);
            this.renderFlightStatus(data.flight_status);
            this.renderSecurityStatus(data.security_status);
            this.renderResourceUtilization(data.resource_utilization);
            this.renderStaffAvailability(data.staff_availability);
            
            // Load and render facilities data
            this.loadFacilitiesData();

            this.updateLastUpdate();
            this.showLoading(false);
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
            this.showLoading(false);
        }
    }

    renderConveyorSystem() {
        if (!this.conveyorData || this.conveyorData.error) return;

        const container = document.getElementById('conveyor-belts-container');
        const performanceContainer = document.getElementById('system-performance');
        
        if (!container || !performanceContainer) return;

        // Render conveyor belts
        container.innerHTML = this.generateConveyorBeltsHTML();
        
        // Render system performance
        performanceContainer.innerHTML = this.generateSystemPerformanceHTML();
        
        // Animate bags on belts
        this.animateConveyorBelts();
    }

    generateConveyorBeltsHTML() {
        if (!this.conveyorData.conveyor_belts) return '<p>No conveyor data available</p>';

        return this.conveyorData.conveyor_belts.map(belt => {
            const statusClass = `status-${belt.status.toLowerCase()}`;
            const healthClass = `health-${belt.health_status.toLowerCase()}`;
            
            // Generate bag HTML
            const bagsHTML = belt.bags_on_belt.map(bag => {
                const bagClass = `bag-item ${bag.priority.toLowerCase()}`;
                const leftPosition = `${bag.position}%`;
                
                return `<div class="${bagClass}" style="left: ${leftPosition};" 
                         title="Bag ${bag.bag_id} - ${bag.flight} to ${bag.destination}"></div>`;
            }).join('');

            // Generate sensor data HTML
            const sensorHTML = this.generateSensorDataHTML(belt.sensor_data);
            const stageOverlay = this.generateStageOverlayHTML(belt);
            const stageTimeline = this.generateStageTimelineHTML(belt);

            return `
                <div class="conveyor-card mb-3">
                    <div class="belt-info">
                        <span><strong>${belt.belt_id}</strong> - ${belt.terminal}</span>
                        <span class="belt-status ${statusClass}">${belt.status}</span>
                    </div>
                    
                    <div class="conveyor-belt">
                        ${stageOverlay}
                        ${bagsHTML}
                    </div>
                    
                    ${stageTimeline}
                    
                    <div class="row mt-2">
                        <div class="col-md-3">
                            <div class="sensor-panel">
                                <small>Speed</small>
                                <div class="sensor-value">${belt.speed.toFixed(1)} m/s</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="sensor-panel">
                                <small>Utilization</small>
                                <div class="sensor-value">${belt.utilization}%</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="sensor-panel">
                                <small>Health</small>
                                <div><span class="health-indicator ${healthClass}"></span>${belt.health_status}</div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="sensor-panel">
                                <small>Efficiency</small>
                                <div class="efficiency-gauge efficiency-${Math.floor(belt.efficiency_score / 15) * 15}">
                                    ${belt.efficiency_score}%
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    ${sensorHTML}
                    
                    ${this.generateIssuesHTML(belt.predicted_issues)}
                </div>
            `;
        }).join('');
    }

    generateSensorDataHTML(sensorData) {
        if (!sensorData) return '';

        let html = '<div class="row mt-2">';
        
        if (sensorData.weight_sensor) {
            const weight = sensorData.weight_sensor;
            html += `
                <div class="col-md-4">
                    <div class="sensor-panel">
                        <small>Weight Sensor</small>
                        <div class="sensor-value">${weight.current_load}%</div>
                        <small>Max: ${weight.max_capacity}%</small>
                    </div>
                </div>
            `;
        }
        
        if (sensorData.temperature_sensor) {
            const temp = sensorData.temperature_sensor;
            html += `
                <div class="col-md-4">
                    <div class="sensor-panel">
                        <small>Temperature</small>
                        <div class="sensor-value">${temp.current_temp.toFixed(1)}°C</div>
                        <small>Max Safe: ${temp.max_safe_temp}°C</small>
                    </div>
                </div>
            `;
        }
        
        if (sensorData.vibration_sensor) {
            const vib = sensorData.vibration_sensor;
            html += `
                <div class="col-md-4">
                    <div class="sensor-panel">
                        <small>Vibration</small>
                        <div class="sensor-value">${vib.vibration_level.toFixed(1)}</div>
                        <small>Bearing: ${vib.bearing_health}</small>
                    </div>
                </div>
            `;
        }
        
        html += '</div>';
        return html;
    }

    generateIssuesHTML(issues) {
        if (!issues || issues.length === 0) return '';
        
        return `
            <div class="mt-2">
                <small class="text-warning"><i class="fas fa-exclamation-triangle me-1"></i>Issues Detected:</small>
                ${issues.map(issue => `
                    <div class="alert alert-warning alert-sm py-1 mt-1">
                        <strong>${issue.type}</strong>: ${issue.description}
                        <br><small>Action: ${issue.recommended_action}</small>
                    </div>
                `).join('')}
            </div>
        `;
    }

    generateSystemPerformanceHTML() {
        if (!this.conveyorData.system_insights) return '<p>No performance data available</p>';
        
        const insights = this.conveyorData.system_insights;
        
        return `
            <div class="text-white">
                <div class="mb-3">
                    <h6>System Efficiency</h6>
                    <div class="sensor-value">${insights.system_efficiency}%</div>
                </div>
                
                <div class="mb-3">
                    <h6>Active Belts</h6>
                    <div class="sensor-value">${insights.active_belts_ratio}%</div>
                </div>
                
                <div class="mb-3">
                    <h6>Critical Issues</h6>
                    <div class="sensor-value">${insights.critical_issues_count}</div>
                </div>
                
                <div class="mb-3">
                    <h6>System Health</h6>
                    <div class="sensor-value">${insights.system_health}</div>
                </div>
                
                <div class="mb-3">
                    <h6>Maintenance Priority</h6>
                    <div class="sensor-value">${insights.maintenance_priority}</div>
                </div>
            </div>
        `;
    }

    renderAIAlerts() {
        const container = document.getElementById('ai-alerts-content-inner');
        if (!container) return;

        const filteredAlerts = this.filterAlertsByScope(this.conveyorData.ai_alerts || []);
        // Update the header to show alert count
        this.updateAlertsHeader(filteredAlerts);

        if (!filteredAlerts.length) {
            container.innerHTML = `
                <div class="no-alerts">
                    <i class="fas fa-check-circle text-success"></i>
                    <h6>All Systems Normal</h6>
                    <p>No active alerts at this time. All conveyor belts are operating efficiently.</p>
                </div>
            `;
            return;
        }

        const alertsHTML = filteredAlerts.map(alert => {
            const alertClass = `ai-alert-item ${alert.priority.toLowerCase()}`;
            const priorityIcon = this.getPriorityIcon(alert.priority);
            
            return `
                <div class="${alertClass}">
                    <div class="ai-alert-header">
                        <div class="ai-alert-type">
                            <i class="${priorityIcon} me-2"></i>${alert.type}
                        </div>
                        <div class="ai-alert-time">
                            ${alert.timestamp}
                        </div>
                    </div>
                    <div class="ai-alert-message">
                        ${alert.message}
                    </div>
                    <div class="ai-alert-actions">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewAlertDetails('${alert.id}')">
                            <i class="fas fa-eye me-1"></i>View Details
                        </button>
                        <button class="btn btn-sm btn-outline-success" onclick="resolveAlert('${alert.id}')">
                            <i class="fas fa-check me-1"></i>Resolve
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = alertsHTML;
    }

    filterAlertsByScope(alerts) {
        if (!Array.isArray(alerts) || !alerts.length) {
            return [];
        }

        return alerts.filter(alert => {
            if (!alert.scope || !Array.isArray(alert.scope) || !alert.scope.length) {
                return true;
            }
            return alert.scope.some(scope => this.alertScopes.includes(scope) || scope === 'all');
        });
    }

    updateAlertsHeader(alerts) {
        const header = document.querySelector('[data-widget="ai-alerts"] .widget-header h5');
        const headerContainer = document.querySelector('[data-widget="ai-alerts"] .widget-header');
        if (!header || !headerContainer) return;

        const alertList = Array.isArray(alerts) ? alerts : (this.conveyorData?.ai_alerts || []);

        if (!alertList.length) {
            header.innerHTML = '<i class="fas fa-exclamation-triangle me-2 text-warning"></i>AI-Powered Alerts & Notifications';
            headerContainer.classList.remove('has-alerts');
            return;
        }

        const totalAlerts = alertList.length;
        const criticalAlerts = alertList.filter(alert => 
            alert.priority.toLowerCase() === 'critical'
        ).length;
        const highAlerts = alertList.filter(alert => 
            alert.priority.toLowerCase() === 'high'
        ).length;

        let alertText = 'AI-Powered Alerts & Notifications';
        
        if (criticalAlerts > 0) {
            alertText += ` <span class="badge bg-danger ms-2">${criticalAlerts} Critical</span>`;
            // Auto-expand if there are critical alerts
            this.autoExpandAlerts();
        }
        if (highAlerts > 0) {
            alertText += ` <span class="badge bg-warning ms-2">${highAlerts} High</span>`;
        }
        if (totalAlerts > 0) {
            alertText += ` <span class="badge bg-info ms-2">${totalAlerts} Total</span>`;
        }

        header.innerHTML = `<i class="fas fa-exclamation-triangle me-2 text-warning"></i>${alertText}`;
        headerContainer.classList.add('has-alerts');
    }

    autoExpandAlerts() {
        const content = document.getElementById('ai-alerts-content');
        const chevron = document.getElementById('ai-alerts-chevron');
        
        if (content && content.style.display === 'none') {
            content.style.display = 'block';
            content.classList.remove('collapsed');
            content.classList.add('expanded');
            
            if (chevron) {
                chevron.classList.add('rotated');
            }
        }
    }

    getPriorityIcon(priority) {
        const icons = {
            'critical': 'fas fa-exclamation-triangle',
            'high': 'fas fa-exclamation-circle',
            'medium': 'fas fa-info-circle',
            'low': 'fas fa-info'
        };
        return icons[priority.toLowerCase()] || 'fas fa-info';
    }

    renderAIInsights() {
        const container = document.getElementById('ai-insights-container');
        if (!container) return;

        if (!this.conveyorData || this.conveyorData.error || !this.conveyorData.system_insights) {
            container.innerHTML = `
                <div class="widget-error">
                    <i class="fas fa-info-circle me-2"></i>AI insights are currently unavailable.
                </div>
            `;
            return;
        }

        const insights = this.conveyorData.system_insights || {};
        const recommendations = Array.isArray(insights.recommendations) ? insights.recommendations : [];
        const performanceMetrics = this.conveyorData.performance_metrics || null;

        container.innerHTML = `
            <div class="ai-insight mb-3">
                <h6><i class="fas fa-lightbulb me-2"></i>System Insights</h6>
                <p class="mb-2">
                    Overall system efficiency is at <strong>${insights.system_efficiency ?? 0}%</strong>
                    with <strong>${insights.active_belts_ratio ?? 0}%</strong> belts active.
                </p>
                <small>Peak performance time: ${insights.peak_performance_time || 'N/A'}</small>
            </div>
            
            ${recommendations.length > 0 ? recommendations.map(rec => `
                <div class="alert alert-info py-2">
                    <i class="fas fa-info-circle me-2"></i>${rec}
                </div>
            `).join('') : `
                <div class="alert alert-secondary py-2">
                    <i class="fas fa-info-circle me-2"></i>No AI recommendations at this time.
                </div>
            `}
            
            <div class="mt-3">
                <h6>Performance Metrics</h6>
                ${performanceMetrics ? `
                    <div class="row">
                        <div class="col-md-6">
                            <small>Speed: ${performanceMetrics.speed_metrics?.average?.toFixed?.(2) || performanceMetrics.speed_metrics?.average || 0} m/s avg</small>
                        </div>
                        <div class="col-md-6">
                            <small>Efficiency: ${performanceMetrics.efficiency_metrics?.average || 0}% avg</small>
                        </div>
                    </div>
                ` : '<small class="text-muted">No performance metrics available.</small>'}
            </div>
        `;
    }

    animateConveyorBelts() {
        // Animate bags moving on conveyor belts
        const bags = document.querySelectorAll('.bag-item');
        
        bags.forEach(bag => {
            const currentLeft = parseFloat(bag.style.left);
            const newLeft = Math.min(100, currentLeft + Math.random() * 2);
            
            bag.style.left = `${newLeft}%`;
            
            // Remove bag if it reaches the end
            if (newLeft >= 100) {
                setTimeout(() => {
                    bag.remove();
                }, 500);
            }
        });
        
        // Continue animation
        setTimeout(() => this.animateConveyorBelts(), 2000);
    }

    renderPassengerFlow(data) {
        const chartEl = document.getElementById('passenger-flow-chart');
        if (!chartEl) return;

        if (!data || data.error) {
            this.renderWidgetError('passenger-flow-chart', data?.error || 'Passenger flow data unavailable');
            this.updateText('current-passengers', '-');
            this.updateText('peak-hour', '-');
            this.updateText('daily-total', '-');
            return;
        }

        const chartData = [data.chart];
        const layout = data.layout;
        
        Plotly.newPlot(chartEl, chartData, layout, {responsive: true});

        // Update metrics
        this.updateText('current-passengers', data.current_hour_passengers);
        this.updateText('peak-hour', data.peak_hour);
        this.updateText('daily-total', data.total_daily);
    }

    renderQueueStatus(data) {
        const chartEl = document.getElementById('queue-status-chart');
        if (!chartEl) return;

        if (!data || data.error) {
            this.renderWidgetError('queue-status-chart', data?.error || 'Queue status data unavailable');
            this.updateText('total-queues', '-');
            this.updateText('avg-wait', '-');
            return;
        }

        const chartData = [data.chart];
        const layout = data.layout;
        
        Plotly.newPlot(chartEl, chartData, layout, {responsive: true});

        // Update metrics
        this.updateText('total-queues', data.total_in_queues);
        this.updateText('avg-wait', Math.round(data.avg_wait_time_overall));
    }

    renderBaggageTracking(data) {
        const chartEl = document.getElementById('baggage-tracking-chart');
        if (!chartEl) return;

        if (!data || data.error) {
            this.renderWidgetError('baggage-tracking-chart', data?.error || 'Baggage tracking data unavailable');
            this.updateText('active-belts', '-');
            this.updateText('live-bags', '-');
            this.updateText('avg-speed', '-');
            this.renderMiniConveyorFlow(this.conveyorData?.conveyor_belts || []);
            return;
        }

        const chartData = [data.chart];
        const layout = data.layout;
        
        Plotly.newPlot(chartEl, chartData, layout, {responsive: true});
        
        // Update metrics
        this.updateText('active-belts', data.active_belts);
        this.updateText('live-bags', data.live_bags_count);
        this.updateText('avg-speed', `${data.avg_belt_speed.toFixed(1)} m/s`);

        this.renderMiniConveyorFlow(data.conveyor_belts);
    }

    renderMiniConveyorFlow(conveyorBelts) {
        const container = document.getElementById('live-conveyors');
        if (!container) return;

        container.innerHTML = this.generateMiniConveyorVisualization(conveyorBelts);
    }

    generateMiniConveyorVisualization(conveyorBelts) {
        const stages = this.getBeltStages();
        if (!stages.length || !Array.isArray(conveyorBelts) || conveyorBelts.length === 0) {
            return '<div class="mini-conveyor-empty text-muted">No live conveyor data available</div>';
        }

        const stageCounts = this.aggregateStageCounts(conveyorBelts);
        const totalBags = Object.values(stageCounts).reduce((sum, value) => sum + value, 0) || 1;
        const dominantStage = this.getDominantStage(stageCounts);

        const stageBarHTML = `
            <div class="mini-conveyor-bar">
                ${stages.map(stage => {
                    const percentage = (stageCounts[stage.id] / totalBags) * 100;
                    const width = Math.max(stageCounts[stage.id] > 0 ? 8 : 0, percentage);
                    const isActive = dominantStage === stage.id ? 'active' : '';
                    return `
                        <div class="mini-conveyor-segment mini-stage-${stage.id} ${isActive}" style="width: ${width}%;">
                            <span>${stageCounts[stage.id] || 0}</span>
                        </div>
                    `;
                }).join('')}
            </div>
        `;

        const stageLegendHTML = `
            <div class="mini-conveyor-legend">
                ${stages.map(stage => `
                    <div class="mini-conveyor-pill mini-stage-${stage.id}">
                        <span class="mini-pill-icon"><i class="${stage.icon}"></i></span>
                        <div>
                            <strong>${stage.label}</strong>
                            <small>${stageCounts[stage.id] || 0} bags</small>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        return `
            <div class="mini-conveyor-visualization">
                ${stageBarHTML}
                ${stageLegendHTML}
            </div>
        `;
    }

    aggregateStageCounts(conveyorBelts) {
        const stages = this.getBeltStages();
        const totals = stages.reduce((acc, stage) => {
            acc[stage.id] = 0;
            return acc;
        }, {});

        if (!Array.isArray(conveyorBelts)) {
            return totals;
        }

        conveyorBelts.forEach(belt => {
            const counts = this.calculateStageCounts(belt);
            stages.forEach(stage => {
                totals[stage.id] += counts[stage.id] || 0;
            });
        });

        return totals;
    }

    async handleDatasetRecovery(data) {
        if (!data || !data.errors) {
            this.notifyDashboardErrors(null);
            return data;
        }

        const errorKeys = Object.keys(data.errors);
        if (errorKeys.length === 0) {
            delete data.errors;
            this.notifyDashboardErrors(null);
            return data;
        }

        await Promise.all(errorKeys.map(async (key) => {
            const endpoint = this.datasetEndpoints[key];
            if (!endpoint) return;

            try {
                const resp = await fetch(`/api/airport/${this.airportCode}/${endpoint}`);
                const dataset = await resp.json();
                data[key] = dataset;
                if (!dataset.error) {
                    delete data.errors[key];
                }
            } catch (error) {
                console.warn(`Failed to recover ${key} dataset`, error);
            }
        }));

        if (data.errors && Object.keys(data.errors).length === 0) {
            delete data.errors;
            this.notifyDashboardErrors(null);
        } else {
            this.notifyDashboardErrors(data.errors);
        }

        return data;
    }

    notifyDashboardErrors(errors) {
        const banner = document.getElementById('dashboard-error-banner');
        const messageEl = document.getElementById('dashboard-error-message');
        if (!banner || !messageEl) return;

        if (!errors || Object.keys(errors).length === 0) {
            banner.classList.add('d-none');
            messageEl.textContent = '';
            return;
        }

        const readable = Object.keys(errors).map(key => key.replace(/_/g, ' '));
        messageEl.textContent = `Some widgets are still loading: ${readable.join(', ')}`;
        banner.classList.remove('d-none');
    }

    renderWidgetError(targetId, message) {
        const container = document.getElementById(targetId);
        if (!container) return;

        container.innerHTML = `
            <div class="widget-error">
                <i class="fas fa-exclamation-triangle me-2"></i>${message || 'Data unavailable'}
            </div>
        `;
    }

    updateText(elementId, value) {
        const el = document.getElementById(elementId);
        if (el) {
            el.textContent = value;
        }
    }

    renderFlightStatus(data) {
        const chartEl = document.getElementById('flight-status-chart');
        if (!chartEl) return;

        if (!data || data.error) {
            this.renderWidgetError('flight-status-chart', data?.error || 'Flight status data unavailable');
            this.renderFlightsTable([]);
            this.updateText('weather-delays', '-');
            this.updateText('on-time-flights', '-');
            this.updateText('total-flights', '-');
            this.hideWeatherAlert();
            return;
        }

        // Render chart
        const chartData = [data.chart];
        const layout = data.layout;
        
        Plotly.newPlot(chartEl, chartData, layout, {responsive: true});
        
        // Render flights table
        this.renderFlightsTable(data.flights);
        
        // Update metrics
        this.updateText('weather-delays', data.weather_delays);
        this.updateText('on-time-flights', data.on_time_flights);
        this.updateText('total-flights', data.total_flights);
        
        // Show weather alert if impact is high
        if (data.weather && data.weather.impact === 'High') {
            this.showWeatherAlert(data.weather);
        } else {
            this.hideWeatherAlert();
        }
    }

    renderFlightsTable(flights) {
        const tbody = document.getElementById('flights-tbody');
        if (!tbody) return;

        if (!flights || flights.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted">
                        <i class="fas fa-info-circle me-1"></i>No flight data available
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = flights.map(flight => `
            <tr>
                <td><strong>${flight.flight_number}</strong><br><small>${flight.airline}</small></td>
                <td>${flight.destination}</td>
                <td>${flight.scheduled_time}</td>
                <td>
                    <span class="badge ${this.getStatusBadgeClass(flight.status)}">
                        ${flight.status}
                    </span>
                </td>
                <td>${flight.gate}</td>
                <td>
                    ${flight.delay_reason ? `<small class="text-danger">${flight.delay_reason}</small>` : '-'}
                </td>
            </tr>
        `).join('');
    }

    getStatusBadgeClass(status) {
        const statusClasses = {
            'On Time': 'bg-success',
            'Delayed': 'bg-warning',
            'Boarding': 'bg-info',
            'Departed': 'bg-secondary',
            'Cancelled': 'bg-danger',
            'Arrived': 'bg-success'
        };
        return statusClasses[status] || 'bg-secondary';
    }

    showWeatherAlert(weather) {
        const alert = document.getElementById('weather-alert');
        if (!alert) return;

        document.getElementById('weather-info').textContent = 
            `${weather.condition}, ${weather.temperature}°C, Wind: ${weather.wind_speed} km/h`;
        document.getElementById('weather-impact').textContent = weather.impact;
        
        alert.style.display = 'block';
        alert.className = `alert ${weather.impact === 'High' ? 'alert-warning' : 'alert-info'} mb-3`;
    }

    hideWeatherAlert() {
        const alert = document.getElementById('weather-alert');
        if (alert) {
            alert.style.display = 'none';
        }
    }

    renderSecurityStatus(data) {
        const chartEl = document.getElementById('security-status-chart');
        if (!chartEl) return;

        if (!data || data.error) {
            this.renderWidgetError('security-status-chart', data?.error || 'Security status data unavailable');
            this.updateText('operational-checkpoints', '-');
            this.updateText('security-staff', '-');
            return;
        }

        const chartData = [data.chart];
        const layout = data.layout;
        
        Plotly.newPlot(chartEl, chartData, layout, {responsive: true});
        
        // Update metrics
        this.updateText('operational-checkpoints', data.operational_checkpoints);
        this.updateText('security-staff', data.total_staff_deployed);
    }

    renderResourceUtilization(data) {
        const chartEl = document.getElementById('resource-utilization-chart');
        if (!chartEl) return;

        if (!data || data.error) {
            this.renderWidgetError('resource-utilization-chart', data?.error || 'Resource utilization data unavailable');
            this.updateText('system-health', '-');
            this.updateText('peak-usage', '-');
            return;
        }

        const chartData = [data.chart];
        const layout = data.layout;
        
        Plotly.newPlot(chartEl, chartData, layout, {responsive: true});
        
        // Update metrics
        this.updateText('system-health', data.overall_health);
        this.updateText('peak-usage', `${data.peak_usage}%`);
    }

    renderStaffAvailability(data) {
        const chartEl = document.getElementById('staff-availability-chart');
        if (!chartEl) return;

        if (!data || data.error) {
            this.renderWidgetError('staff-availability-chart', data?.error || 'Staff availability data unavailable');
            this.updateText('available-staff', '-');
            this.updateText('overall-availability', '-');
            return;
        }

        const chartData = [data.chart];
        const layout = data.layout;
        
        Plotly.newPlot(chartEl, chartData, layout, {responsive: true});
        
        // Update metrics
        this.updateText('available-staff', data.available_staff);
        this.updateText('overall-availability', `${data.overall_availability}%`);
    }

    setupAutoRefresh() {
        setInterval(() => {
            this.loadAllData();
            }, this.refreshInterval);
        }

    updateLastUpdate() {
        const now = new Date();
        document.getElementById('last-update').textContent = now.toLocaleTimeString();
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
    }

    showError(message) {
        // Show error message to user
        console.error(message);
        // You can implement a toast notification system here
    }

    toggleTheme() {
        document.body.classList.toggle('dark-theme');
        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.className = document.body.classList.contains('dark-theme') ? 
                'fas fa-sun' : 'fas fa-moon';
        }
    }

    async loadFacilitiesData() {
        try {
            const response = await fetch(`/api/airport/${this.airportCode}/facilities`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.renderFacilities(data);
        } catch (error) {
            console.error('Error loading facilities data:', error);
            this.showError('Failed to load facilities data');
        }
    }

    renderFacilities(data) {
        const terminalsDiv = document.getElementById('dashboard-terminals-gates');
        const servicesDiv = document.getElementById('dashboard-services');
        const summaryDiv = document.getElementById('facility-summary');
        
        if (!terminalsDiv || !servicesDiv || !summaryDiv) return;

        // Render terminals and gates
        let terminalsHtml = '<div class="row">';
        data.facilities.terminals.forEach(terminal => {
            const gates = data.facilities.gates[terminal] || [];
            const airlines = data.facilities.airlines[terminal] || [];
            terminalsHtml += `
                <div class="col-md-6 mb-2">
                    <div class="card border-info">
                        <div class="card-header bg-info text-white py-2">
                            <h6 class="mb-0"><i class="fas fa-terminal me-2"></i>${terminal}</h6>
                        </div>
                        <div class="card-body py-2">
                            <p class="mb-1"><strong><i class="fas fa-door-open me-1"></i>Gates:</strong></p>
                            <p class="text-muted small mb-2">${gates.join(', ')}</p>
                            <p class="mb-1"><strong><i class="fas fa-plane me-1"></i>Airlines:</strong></p>
                            <p class="text-muted small">${airlines.join(', ')}</p>
                        </div>
                    </div>
                </div>
            `;
        });
        terminalsHtml += '</div>';
        terminalsDiv.innerHTML = terminalsHtml;

        // Render services
        let servicesHtml = '<div class="row">';
        
        // Washrooms section
        servicesHtml += `
            <div class="col-md-6 mb-2">
                <div class="card border-success">
                    <div class="card-header bg-success text-white py-2">
                        <h6 class="mb-0"><i class="fas fa-restroom me-2"></i>Washrooms (${data.facilities.washrooms.length})</h6>
                    </div>
                    <div class="card-body py-2">
                        <ul class="list-unstyled mb-0">
        `;
        data.facilities.washrooms.slice(0, 3).forEach(washroom => {
            const statusColor = washroom.status === 'Available' ? 'text-success' : 'text-warning';
            servicesHtml += `
                <li class="mb-1">
                    <i class="fas fa-map-marker-alt text-primary me-1"></i>
                    <strong>${washroom.location}</strong>
                    <br><span class="text-muted small">Type: ${washroom.type}</span>
                    <br><span class="${statusColor} small"><i class="fas fa-circle me-1"></i>${washroom.status}</span>
                </li>
            `;
        });
        if (data.facilities.washrooms.length > 3) {
            servicesHtml += `<li class="text-muted small">+${data.facilities.washrooms.length - 3} more...</li>`;
        }
        servicesHtml += `
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        // Services section
        servicesHtml += `
            <div class="col-md-6 mb-2">
                <div class="card border-primary">
                    <div class="card-header bg-primary text-white py-2">
                        <h6 class="mb-0"><i class="fas fa-concierge-bell me-2"></i>Services (${data.facilities.services.length})</h6>
                    </div>
                    <div class="card-body py-2">
                        <ul class="list-unstyled mb-0">
        `;
        data.facilities.services.slice(0, 3).forEach(service => {
            servicesHtml += `
                <li class="mb-2">
                    <div class="d-flex align-items-start">
                        <i class="fas fa-star text-warning me-1 mt-1"></i>
                        <div>
                            <strong>${service.name}</strong>
                            <br><span class="text-muted small"><i class="fas fa-map-marker-alt me-1"></i>${service.location}</span>
                            <br><span class="text-info small"><i class="fas fa-clock me-1"></i>${service.hours}</span>
                        </div>
                    </div>
                </li>
            `;
        });
        if (data.facilities.services.length > 3) {
            servicesHtml += `<li class="text-muted small">+${data.facilities.services.length - 3} more...</li>`;
        }
        servicesHtml += `
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        servicesHtml += '</div>';
        servicesDiv.innerHTML = servicesHtml;

        // Update summary statistics
        const summaryItems = summaryDiv.querySelectorAll('h4');
        if (summaryItems.length >= 4) {
            summaryItems[0].textContent = data.total_terminals;
            summaryItems[1].textContent = data.total_gates;
            summaryItems[2].textContent = data.airlines_count;
            summaryItems[3].textContent = data.facilities.washrooms.length + data.facilities.services.length;
        }
    }
}

// Global functions for widget interactions
function refreshWidget(widgetName) {
    // Implement individual widget refresh
    console.log(`Refreshing widget: ${widgetName}`);
    
    if (widgetName === 'facilities' && window.dashboard) {
        window.dashboard.loadFacilitiesData();
    }
}

function refreshAllData() {
    if (window.dashboard) {
        window.dashboard.loadAllData();
    }
}

function toggleFullscreen(button) {
    const widget = button.closest('.dashboard-widget');
    if (widget) {
        widget.classList.toggle('fullscreen');
    const icon = button.querySelector('i');
        icon.className = widget.classList.contains('fullscreen') ? 
            'fas fa-compress' : 'fas fa-expand';
    }
}

// Initialize dashboard when DOM is loaded
function initializeDashboard(airportCode) {
    window.dashboard = new AirportDashboard(airportCode);
}

// Alert action functions
function viewAlertDetails(alertId) {
    console.log(`Viewing details for alert: ${alertId}`);
    // You can implement a modal or detailed view here
    alert(`Viewing details for alert: ${alertId}`);
}

function resolveAlert(alertId) {
    console.log(`Resolving alert: ${alertId}`);
    // You can implement alert resolution logic here
    alert(`Alert ${alertId} has been resolved`);
    
    // Refresh the dashboard to update alerts
    if (window.dashboard) {
        window.dashboard.loadAllData();
    }
}

// Widget content toggle function
function toggleWidgetContent(widgetName) {
    const contentId = `${widgetName}-content`;
    const content = document.getElementById(contentId);
    const chevron = document.getElementById(`${widgetName}-chevron`);
    
    if (!content) return;
    
    if (content.style.display === 'none' || content.classList.contains('collapsed')) {
        // Expand the widget
        content.style.display = 'block';
        content.classList.remove('collapsed');
        content.classList.add('expanded');
        
        if (chevron) {
            chevron.classList.add('rotated');
        }
    } else {
        // Collapse the widget
        content.classList.remove('expanded');
        content.classList.add('collapsed');
        
        if (chevron) {
            chevron.classList.remove('rotated');
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AirportDashboard;
}
