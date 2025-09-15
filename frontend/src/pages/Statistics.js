import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import apiService from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

function Statistics() {
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      const response = await apiService.getStatistics();
      setStatistics(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load statistics');
      console.error('Error fetching statistics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  // Prepare data for charts
  const projectData = statistics?.by_project?.map((p) => ({
    name: p.project_id || 'Unknown',
    submissions: p.count,
  })) || [];

  const concentrationData = statistics?.concentration_stats ? [
    { name: 'Min', value: statistics.concentration_stats.min_concentration },
    { name: 'Avg', value: statistics.concentration_stats.avg_concentration },
    { name: 'Max', value: statistics.concentration_stats.max_concentration },
  ] : [];

  // Prepare timeline data from recent submissions
  const timelineData = statistics?.recent_submissions?.map((sub) => ({
    date: new Date(sub.scanned_at).toLocaleDateString(),
    project: sub.project_id,
  })).reduce((acc, curr) => {
    const existing = acc.find(item => item.date === curr.date);
    if (existing) {
      existing.count++;
    } else {
      acc.push({ date: curr.date, count: 1 });
    }
    return acc;
  }, []) || [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Statistics & Analytics
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Comprehensive overview of submission data and trends
      </Typography>

      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Submissions
              </Typography>
              <Typography variant="h3">
                {statistics?.total_submissions || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Samples
              </Typography>
              <Typography variant="h3">
                {statistics?.total_samples || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Unique Projects
              </Typography>
              <Typography variant="h3">
                {statistics?.unique_projects || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Samples/Submission
              </Typography>
              <Typography variant="h3">
                {statistics?.total_submissions > 0
                  ? Math.round(statistics.total_samples / statistics.total_submissions)
                  : 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Submissions by Project */}
        {projectData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Submissions by Project
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={projectData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="name" 
                    angle={-45}
                    textAnchor="end"
                    height={100}
                  />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="submissions" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        )}

        {/* Project Distribution Pie Chart */}
        {projectData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Project Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={projectData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${entry.submissions}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="submissions"
                  >
                    {projectData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        )}

        {/* Concentration Statistics */}
        {concentrationData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Concentration Statistics (ng/µL)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={concentrationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => `${value.toFixed(2)} ng/µL`} />
                  <Bar dataKey="value" fill="#00C49F" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        )}

        {/* Submission Timeline */}
        {timelineData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Recent Submission Timeline
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timelineData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line 
                    type="monotone" 
                    dataKey="count" 
                    stroke="#8884d8" 
                    strokeWidth={2}
                    dot={{ fill: '#8884d8' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        )}

        {/* Detailed Statistics */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Detailed Statistics
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1" color="primary" gutterBottom>
                  Sample Concentration Range
                </Typography>
                <Typography variant="body2">
                  Minimum: {statistics?.concentration_stats?.min_concentration?.toFixed(2) || 'N/A'} ng/µL
                </Typography>
                <Typography variant="body2">
                  Average: {statistics?.concentration_stats?.avg_concentration?.toFixed(2) || 'N/A'} ng/µL
                </Typography>
                <Typography variant="body2">
                  Maximum: {statistics?.concentration_stats?.max_concentration?.toFixed(2) || 'N/A'} ng/µL
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1" color="primary" gutterBottom>
                  Submission Frequency
                </Typography>
                <Typography variant="body2">
                  Total Submissions: {statistics?.total_submissions || 0}
                </Typography>
                <Typography variant="body2">
                  Active Projects: {statistics?.unique_projects || 0}
                </Typography>
                <Typography variant="body2">
                  Avg Samples per Submission: {
                    statistics?.total_submissions > 0
                      ? (statistics.total_samples / statistics.total_submissions).toFixed(1)
                      : 0
                  }
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="subtitle1" color="primary" gutterBottom>
                  Database Summary
                </Typography>
                <Typography variant="body2">
                  Total Records: {statistics?.total_submissions || 0}
                </Typography>
                <Typography variant="body2">
                  Total Sample Data Points: {statistics?.total_samples || 0}
                </Typography>
                <Typography variant="body2">
                  Database Status: Active
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Statistics;
