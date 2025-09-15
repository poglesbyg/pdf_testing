import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Button,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Card,
  CardContent,
  IconButton,
} from '@mui/material';
import {
  ArrowBack as BackIcon,
  Download as DownloadIcon,
  Science as ScienceIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import apiService from '../services/api';

function SubmissionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [submission, setSubmission] = useState(null);
  const [samples, setSamples] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    fetchSubmissionDetails();
    fetchSamples();
  }, [id]);

  const fetchSubmissionDetails = async () => {
    try {
      setLoading(true);
      const response = await apiService.getSubmission(id);
      setSubmission(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load submission details');
      console.error('Error fetching submission:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSamples = async () => {
    try {
      const response = await apiService.getSamples(id);
      setSamples(response.data);
    } catch (err) {
      console.error('Error fetching samples:', err);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleExportSamples = () => {
    if (!samples || !samples.samples) return;
    
    const dataStr = JSON.stringify(samples.samples, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `samples_${id}_${Date.now()}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
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
      <Box>
        <Button
          startIcon={<BackIcon />}
          onClick={() => navigate('/submissions')}
          sx={{ mb: 2 }}
        >
          Back to Submissions
        </Button>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!submission) {
    return (
      <Box>
        <Button
          startIcon={<BackIcon />}
          onClick={() => navigate('/submissions')}
          sx={{ mb: 2 }}
        >
          Back to Submissions
        </Button>
        <Alert severity="warning">Submission not found</Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <IconButton onClick={() => navigate('/submissions')}>
            <BackIcon />
          </IconButton>
          <Typography variant="h4">
            Submission Details
          </Typography>
        </Box>
        <Chip
          label={submission.short_ref}
          color="primary"
          icon={<DescriptionIcon />}
        />
      </Box>

      <Grid container spacing={3}>
        {/* Submission Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Submission Information
              </Typography>
              <Divider sx={{ my: 2 }} />
              <List dense>
                <ListItem>
                  <ListItemText
                    primary="Submission ID"
                    secondary={submission.submission_id}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="UUID"
                    secondary={submission.uuid}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="File Hash"
                    secondary={
                      <Typography variant="caption" sx={{ wordBreak: 'break-all' }}>
                        {submission.file_hash}
                      </Typography>
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="PDF File"
                    secondary={submission.pdf_filename || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Scanned At"
                    secondary={format(new Date(submission.scanned_at), 'PPpp')}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Created At"
                    secondary={format(new Date(submission.created_at), 'PPpp')}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Project Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Project Information
              </Typography>
              <Divider sx={{ my: 2 }} />
              <List dense>
                <ListItem>
                  <ListItemText
                    primary="Project ID"
                    secondary={submission.project_id || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Owner"
                    secondary={submission.owner || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Source Organism"
                    secondary={submission.source_organism || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Sequencing Type"
                    secondary={submission.sequencing_type || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Sample Type"
                    secondary={submission.sample_type || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Total Samples"
                    secondary={submission.total_samples || 0}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Additional Information */}
        {submission.additional_info && Object.keys(submission.additional_info).length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Additional Information
                </Typography>
                <Divider sx={{ my: 2 }} />
                <Grid container spacing={2}>
                  {Object.entries(submission.additional_info).map(([key, value]) => (
                    <Grid item xs={12} sm={6} md={4} key={key}>
                      <Typography variant="subtitle2" color="textSecondary">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Typography>
                      <Typography variant="body2">
                        {typeof value === 'object' ? JSON.stringify(value) : value}
                      </Typography>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Sample Statistics */}
        {samples && samples.statistics && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6" gutterBottom>
                    Sample Statistics
                  </Typography>
                  <ScienceIcon color="primary" />
                </Box>
                <Divider sx={{ my: 2 }} />
                <Grid container spacing={3}>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Total Samples
                    </Typography>
                    <Typography variant="h6">
                      {samples.statistics.total}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Average Concentration
                    </Typography>
                    <Typography variant="h6">
                      {samples.statistics.avg_concentration.toFixed(2)} ng/µL
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Min Concentration
                    </Typography>
                    <Typography variant="h6">
                      {samples.statistics.min_concentration.toFixed(2)} ng/µL
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="subtitle2" color="textSecondary">
                      Max Concentration
                    </Typography>
                    <Typography variant="h6">
                      {samples.statistics.max_concentration.toFixed(2)} ng/µL
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Samples Table */}
        {samples && samples.samples && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Sample Details
                </Typography>
                <Button
                  startIcon={<DownloadIcon />}
                  onClick={handleExportSamples}
                  variant="outlined"
                  size="small"
                >
                  Export Samples
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Sample Name</TableCell>
                      <TableCell align="right">Volume (µL)</TableCell>
                      <TableCell align="right">Qubit Conc. (ng/µL)</TableCell>
                      <TableCell align="right">Nanodrop Conc. (ng/µL)</TableCell>
                      <TableCell align="right">A260/280 Ratio</TableCell>
                      <TableCell align="right">A260/230 Ratio</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {samples.samples
                      .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                      .map((sample, index) => (
                        <TableRow key={index} hover>
                          <TableCell>{sample.sample_name}</TableCell>
                          <TableCell align="right">{sample.volume_ul.toFixed(1)}</TableCell>
                          <TableCell align="right">{sample.qubit_conc.toFixed(2)}</TableCell>
                          <TableCell align="right">{sample.nanodrop_conc.toFixed(2)}</TableCell>
                          <TableCell align="right">{sample.a260_280_ratio.toFixed(2)}</TableCell>
                          <TableCell align="right">
                            {sample.a260_230_ratio ? sample.a260_230_ratio.toFixed(2) : 'N/A'}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <TablePagination
                rowsPerPageOptions={[5, 10, 25, 50]}
                component="div"
                count={samples.samples.length}
                rowsPerPage={rowsPerPage}
                page={page}
                onPageChange={handleChangePage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default SubmissionDetail;
