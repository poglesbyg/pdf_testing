import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  IconButton,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText,
  TextField,
  MenuItem,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import {
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { useSnackbar } from 'notistack';
import apiService from '../services/api';

function Submissions() {
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteDialog, setDeleteDialog] = useState({ open: false, submission: null });
  const [filterProject, setFilterProject] = useState('');
  const [projects, setProjects] = useState([]);
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    fetchSubmissions();
    fetchProjects();
  }, [filterProject]);

  const fetchSubmissions = async () => {
    try {
      setLoading(true);
      const response = await apiService.getSubmissions(filterProject || null);
      setSubmissions(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load submissions');
      console.error('Error fetching submissions:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await apiService.getProjects();
      setProjects(response.data.projects || []);
    } catch (err) {
      console.error('Error fetching projects:', err);
    }
  };

  const handleView = (submissionId) => {
    navigate(`/submissions/${submissionId}`);
  };

  const handleDelete = async () => {
    if (!deleteDialog.submission) return;

    try {
      await apiService.deleteSubmission(deleteDialog.submission.submission_id);
      enqueueSnackbar('Submission deleted successfully', { variant: 'success' });
      setDeleteDialog({ open: false, submission: null });
      fetchSubmissions();
    } catch (err) {
      enqueueSnackbar('Failed to delete submission', { variant: 'error' });
      console.error('Error deleting submission:', err);
    }
  };

  const handleExport = async () => {
    try {
      const response = await apiService.exportDatabase('json');
      const blob = new Blob([response.data], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `submissions_export_${format(new Date(), 'yyyyMMdd_HHmmss')}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      enqueueSnackbar('Export completed successfully', { variant: 'success' });
    } catch (err) {
      enqueueSnackbar('Failed to export data', { variant: 'error' });
      console.error('Error exporting data:', err);
    }
  };

  const columns = [
    {
      field: 'submission_id',
      headerName: 'Submission ID',
      flex: 1,
      minWidth: 200,
    },
    {
      field: 'short_ref',
      headerName: 'Reference',
      width: 120,
      renderCell: (params) => (
        <Chip label={params.value} size="small" variant="outlined" />
      ),
    },
    {
      field: 'project_id',
      headerName: 'Project',
      flex: 1,
      minWidth: 150,
      renderCell: (params) => params.value || 'N/A',
    },
    {
      field: 'owner',
      headerName: 'Owner',
      flex: 1,
      minWidth: 200,
      renderCell: (params) => params.value || 'N/A',
    },
    {
      field: 'total_samples',
      headerName: 'Samples',
      width: 100,
      type: 'number',
    },
    {
      field: 'scanned_at',
      headerName: 'Scanned',
      flex: 1,
      minWidth: 180,
      renderCell: (params) => {
        if (!params.value) return 'N/A';
        return format(new Date(params.value), 'MMM dd, yyyy HH:mm');
      },
    },
    {
      field: 'pdf_filename',
      headerName: 'File',
      flex: 1,
      minWidth: 200,
      renderCell: (params) => (
        <Typography variant="body2" sx={{ 
          overflow: 'hidden', 
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        }}>
          {params.value || 'N/A'}
        </Typography>
      ),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 120,
      sortable: false,
      renderCell: (params) => (
        <Box>
          <IconButton
            size="small"
            onClick={() => handleView(params.row.submission_id)}
            title="View details"
          >
            <ViewIcon fontSize="small" />
          </IconButton>
          <IconButton
            size="small"
            onClick={() => setDeleteDialog({ open: true, submission: params.row })}
            title="Delete"
            color="error"
          >
            <DeleteIcon fontSize="small" />
          </IconButton>
        </Box>
      ),
    },
  ];

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

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Submissions
          </Typography>
          <Typography variant="body1" color="textSecondary">
            Manage all PDF submissions
          </Typography>
        </Box>
        <Box display="flex" gap={2} alignItems="center">
          <TextField
            select
            label="Filter by Project"
            value={filterProject}
            onChange={(e) => setFilterProject(e.target.value)}
            size="small"
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="">All Projects</MenuItem>
            {projects.map((project) => (
              <MenuItem key={project.project_id} value={project.project_id}>
                {project.project_id} ({project.count})
              </MenuItem>
            ))}
          </TextField>
          <IconButton onClick={fetchSubmissions} title="Refresh">
            <RefreshIcon />
          </IconButton>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={handleExport}
          >
            Export
          </Button>
        </Box>
      </Box>

      <Paper sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={submissions}
          columns={columns}
          getRowId={(row) => row.submission_id}
          pageSize={10}
          rowsPerPageOptions={[10, 25, 50]}
          checkboxSelection={false}
          disableSelectionOnClick
          sx={{
            '& .MuiDataGrid-cell:hover': {
              cursor: 'pointer',
            },
          }}
          onRowClick={(params) => handleView(params.row.submission_id)}
        />
      </Paper>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, submission: null })}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete submission{' '}
            <strong>{deleteDialog.submission?.submission_id}</strong>? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, submission: null })}>
            Cancel
          </Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default Submissions;
