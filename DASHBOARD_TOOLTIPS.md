# CATDAMS Dashboard Tooltips and UI Documentation

## Overview

This document provides comprehensive guidance for dashboard tooltips, user interface elements, and help text to ensure users understand the TDC modules and their outputs.

## TDC Module Tooltips

### TDC-AI1: Risk Analysis
**Tooltip**: "Risk Analysis - Overall threat assessment combining user and AI analysis"
**Detailed Description**: 
- Analyzes both user vulnerabilities and AI manipulation attempts
- Provides a combined risk score and escalation recommendations
- Uses Azure OpenAI for comprehensive analysis
- Outputs standardized ModuleOutput schema with evidence

### TDC-AI2: AI Response
**Tooltip**: "AI Response - Detects manipulative AI responses using Azure OpenAI"
**Detailed Description**:
- Always analyzes non-empty AI responses for manipulation tactics
- Uses keyword detection as initial triggers
- Identifies emotional manipulation, trust-baiting, and safety concerns
- Returns detailed evidence of manipulation attempts

### TDC-AI3: User Vulnerability
**Tooltip**: "User Vulnerability - Temporal analysis of user susceptibility across timeframes"
**Detailed Description**:
- Analyzes user vulnerability across short, medium, and long-term timeframes
- Tracks escalation patterns and adaptation behavior
- Identifies emotional instability, dependency, and isolation tendencies
- Provides vulnerability scoring and intervention recommendations

### TDC-AI4: Deep Synthesis
**Tooltip**: "Deep Synthesis - Comprehensive threat synthesis from all modules"
**Detailed Description**:
- Synthesizes intelligence from all TDC modules
- Identifies escalation patterns and interaction dynamics
- Provides priority recommendations and resource allocation
- Combines cross-module evidence for complete threat assessment

### TDC-AI5: LLM Influence
**Tooltip**: "LLM Influence - Detects subtle AI manipulation and conditioning"
**Detailed Description**:
- Detects subtle AI manipulation and conditioning patterns
- Identifies long-term influence operations and behavioral conditioning
- Analyzes escalation patterns in AI behavior
- Detects role-playing attempts and adaptation strategies

### TDC-AI6: Pattern Classification
**Tooltip**: "Pattern Classification - Sentiment and pattern analysis for both user and AI"
**Detailed Description**:
- Analyzes sentiment and patterns for both user and AI messages
- Detects emotional manipulation and psychological impact
- Identifies vulnerability exploitation and manipulation tactics
- Provides pattern matching and behavioral analysis

### TDC-AI7: Explainability
**Tooltip**: "Explainability - Generates human-readable explanations and evidence"
**Detailed Description**:
- Generates human-readable explanations for all TDC module outputs
- Provides compliance and audit trail documentation
- Collects evidence and trust indicators
- Ensures transparency and accountability

### TDC-AI8: Synthesis
**Tooltip**: "Synthesis - Final synthesis and actionable recommendations"
**Detailed Description**:
- Provides final synthesis and actionable recommendations
- Resolves conflicts between module outputs
- Prioritizes threats and provides escalation paths
- Generates actionable recommendations and resource allocation

## Dashboard Element Tooltips

### Summary Cards

#### Total Sessions
**Tooltip**: "Number of monitored chat sessions"
**Help Text**: "Shows the total number of active and completed chat sessions being monitored by CATDAMS."

#### Total Events
**Tooltip**: "Number of detected events"
**Help Text**: "Displays the total number of events (messages, interactions) processed by the system."

#### Avg Events/Session
**Tooltip**: "Average number of events per session"
**Help Text**: "Shows the average number of events (messages, interactions) per monitored session."

#### Total Threats
**Tooltip**: "Number of detected threats"
**Help Text**: "Displays the total number of threats detected across all sessions."

#### Critical Threats
**Tooltip**: "Number of critical threats requiring immediate attention"
**Help Text**: "Shows threats classified as 'Critical' severity that require immediate intervention."

#### Avg Threat Score
**Tooltip**: "Average threat score across all sessions"
**Help Text**: "Displays the average normalized threat score (0-1) across all monitored sessions."

### Filter Controls

#### Threat Type Filter
**Tooltip**: "Filter by specific threat types detected"
**Options**:
- **AI Manipulation**: "AI attempting to manipulate user behavior"
- **Elicitation**: "Attempts to extract sensitive information"
- **Insider Threat**: "Internal security threats"
- **Sentiment Manipulation**: "Emotional manipulation attempts"
- **Grooming**: "Long-term manipulation tactics"

#### Severity Filter
**Tooltip**: "Filter by threat severity level"
**Options**:
- **Critical**: "Immediate action required"
- **High**: "High priority investigation needed"
- **Medium**: "Monitor and investigate"
- **Low**: "Low risk, continue monitoring"

#### TDC Module Filter
**Tooltip**: "Filter by TDC AI analysis modules"
**Options**: See TDC Module Tooltips above

#### Time Range Filter
**Tooltip**: "Filter events by time range"
**Options**:
- **Last Hour**: "Events from the past hour"
- **Last 24 Hours**: "Events from the past 24 hours"
- **Last 7 Days**: "Events from the past week"
- **Last 30 Days**: "Events from the past month"

#### Sort By Filter
**Tooltip**: "Sort events by different criteria"
**Options**:
- **Newest First**: "Most recent events first"
- **Oldest First**: "Earliest events first"
- **Severity (High-Low)**: "Highest severity first"
- **Severity (Low-High)**: "Lowest severity first"
- **Session ID**: "Alphabetical by session ID"

#### View Mode Filter
**Tooltip**: "Change view mode"
**Options**:
- **Cards**: "Display as expandable cards"
- **Table**: "Display as compact table"
- **Compact**: "Minimal information display"

### Action Buttons

#### Export
**Tooltip**: "Export Data (Ctrl+E)"
**Help Text**: "Export current filtered data to CSV, JSON, or PDF format."

#### Refresh
**Tooltip**: "Refresh Data (Ctrl+R)"
**Help Text**: "Reload all data from the server to get the latest updates."

#### Help
**Tooltip**: "Show Help (F1)"
**Help Text**: "Display comprehensive help documentation and user guide."

#### Expand All Modules
**Tooltip**: "Expand All Modules (Ctrl+Up)"
**Help Text**: "Expand all TDC module cards to show detailed information."

#### Collapse All Modules
**Tooltip**: "Collapse All Modules (Ctrl+Down)"
**Help Text**: "Collapse all TDC module cards to show only summaries."

#### Clear Filters
**Tooltip**: "Clear All Filters"
**Help Text**: "Reset all active filters to show all data."

#### Save Preset
**Tooltip**: "Save Current Filter Preset"
**Help Text**: "Save the current filter configuration for later use."

#### Load Preset
**Tooltip**: "Load Saved Filter Preset"
**Help Text**: "Load a previously saved filter configuration."

## Module Output Display

### Score Display
**Tooltip**: "Normalized risk score (0-100%)"
**Color Coding**:
- **Red (70-100%)**: "High risk - Immediate attention required"
- **Orange (40-69%)**: "Medium risk - Monitor closely"
- **Green (0-39%)**: "Low risk - Continue monitoring"

### Confidence Display
**Tooltip**: "Confidence level in the analysis (0-100%)"
**Color Coding**:
- **Green (80-100%)**: "High confidence - Reliable analysis"
- **Orange (50-79%)**: "Medium confidence - Use with caution"
- **Gray (0-49%)**: "Low confidence - Verify results"

### Recommended Action
**Tooltip**: "Suggested action based on analysis"
**Actions**:
- **Immediate_Intervention**: "Critical threat - Immediate action required"
- **Escalate**: "High risk - Escalate to security team"
- **Monitor**: "Medium risk - Continue monitoring"
- **Investigate**: "Suspicious activity - Investigate further"
- **Review**: "Low risk - Review for context"

### Flags Display
**Tooltip**: "Detected threat indicators or flags"
**Help Text**: "Shows specific threat indicators detected by the module. Hover for detailed descriptions."

### Schema Version
**Tooltip**: "ModuleOutput schema version"
**Help Text**: "Indicates the version of the standardized output schema used by this module."

## Chart Tooltips

### Threat Level Distribution
**Tooltip**: "Distribution of threats by severity level"
**Chart Types**:
- **Doughnut**: "Circular chart showing threat distribution"
- **Bar**: "Bar chart showing threat counts by severity"

### Top Threat Vectors
**Tooltip**: "Most common threat types detected"
**Chart Types**:
- **Bar**: "Bar chart showing threat vector frequency"
- **Line**: "Line chart showing threat vector trends over time"

## Alert Banner

### Critical Threat Alert
**Tooltip**: "Critical threat detected requiring immediate attention"
**Help Text**: "This banner appears when a critical threat is detected. Click for details and recommended actions."

## Session Information

### Session ID
**Tooltip**: "Unique identifier for this chat session"
**Help Text**: "Click to view detailed session conversation and analysis history."

### Active Sessions
**Tooltip**: "Number of currently active sessions"
**Help Text**: "Shows the number of sessions currently being monitored in real-time."

### Pending Alerts
**Tooltip**: "Number of alerts awaiting review"
**Help Text**: "Shows the number of threat alerts that require review or action."

## Keyboard Shortcuts

### Navigation
- **F1**: Show help documentation
- **Ctrl+E**: Export current data
- **Ctrl+R**: Refresh data
- **Ctrl+Up**: Expand all modules
- **Ctrl+Down**: Collapse all modules
- **Escape**: Close modals and dialogs

### Filtering
- **Ctrl+F**: Focus on search box
- **Ctrl+Shift+F**: Clear all filters
- **Tab**: Navigate between filter controls

## Accessibility Features

### Screen Reader Support
- All interactive elements have proper ARIA labels
- TDC module cards include descriptive text for screen readers
- Chart data is available in tabular format for screen readers

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Tab order follows logical flow
- Focus indicators are clearly visible

### Color Contrast
- All text meets WCAG AA contrast requirements
- Color coding is supplemented with text labels
- High contrast mode available

## Performance Tips

### Optimizing Dashboard Performance
- Use filters to reduce data load
- Collapse unused module cards
- Refresh data periodically rather than continuously
- Export large datasets instead of viewing in browser

### Troubleshooting Display Issues
- Clear browser cache if modules don't load
- Check WebSocket connection status
- Verify JavaScript is enabled
- Use browser developer tools to check for errors

## Best Practices

### Using the Dashboard Effectively
1. **Start with Overview**: Check summary cards for high-level metrics
2. **Filter Strategically**: Use filters to focus on specific threats or time periods
3. **Monitor TDC Modules**: Expand module cards to understand detailed analysis
4. **Follow Up on Alerts**: Respond to critical alerts immediately
5. **Export for Analysis**: Export data for detailed offline analysis

### Interpreting Module Outputs
1. **Check Scores**: Higher scores indicate greater risk
2. **Review Confidence**: Higher confidence means more reliable analysis
3. **Examine Evidence**: Look at evidence for specific threat indicators
4. **Consider Context**: Review conversation context for full understanding
5. **Follow Recommendations**: Take recommended actions based on analysis

### Maintaining System Health
1. **Monitor Performance**: Watch for slow response times
2. **Check Connections**: Ensure WebSocket and API connections are stable
3. **Review Logs**: Check system logs for errors or warnings
4. **Update Regularly**: Keep system and modules updated
5. **Backup Data**: Regularly export and backup important data 