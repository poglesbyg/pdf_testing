import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Card,
  CardContent,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  IconButton,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Close as CloseIcon,
  Description as FileIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import apiService from '../services/api';

function Upload() {
  const [file, setFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const uploadedFile = acceptedFiles[0];
      if (uploadedFile.type === 'application/pdf') {
        setFile(uploadedFile);
        setError(null);
        setResult(null);
      } else {
        setError('Please upload a PDF file');
        enqueueSnackbar('Please upload a PDF file', { variant: 'error' });
      }
    }
  }, [enqueueSnackbar]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: false,
  });

  const handleUpload = async () => {
    if (!file) {
      enqueueSnackbar('Please select a file first', { variant: 'warning' });
      return;
    }

    setProcessing(true);
    setError(null);
    setResult(null);

    try {
      const response = await apiService.processPDF(file, true);
      const data = response.data;
      
      setResult(data);
      
      if (data.success) {
        if (data.is_duplicate) {
          enqueueSnackbar('Duplicate PDF detected!', { variant: 'warning' });
        } else {
          enqueueSnackbar('PDF processed successfully!', { variant: 'success' });
        }
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to process PDF';
      setError(errorMessage);
      enqueueSnackbar(errorMessage, { variant: 'error' });
    } finally {
      setProcessing(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  const handleViewSubmission = () => {
    if (result?.submission_id) {
      navigate(`/submissions/${result.submission_id}`);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload PDF Submission
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Upload HTSF Nanopore submission forms for processing
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        {!file && !result && (
          <Box
            {...getRootProps()}
            sx={{
              border: '2px dashed',
              borderColor: isDragActive ? 'primary.main' : 'divider',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              bgcolor: isDragActive ? 'action.hover' : 'background.paper',
              transition: 'all 0.3s',
              '&:hover': {
                bgcolor: 'action.hover',
                borderColor: 'primary.main',
              },
            }}
          >
            <input {...getInputProps()} />
            <UploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              {isDragActive ? 'Drop the PDF here' : 'Drag & drop a PDF file here'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              or click to select a file
            </Typography>
            <Button variant="contained" sx={{ mt: 2 }}>
              Select PDF File
            </Button>
          </Box>
        )}

        {file && !result && (
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box display="flex" alignItems="center">
                  <FileIcon sx={{ mr: 2, color: 'primary.main' }} />
                  <Box>
                    <Typography variant="h6">{file.name}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      Size: {(file.size / 1024 / 1024).toFixed(2)} MB
                    </Typography>
                  </Box>
                </Box>
                <IconButton onClick={handleReset} disabled={processing}>
                  <CloseIcon />
                </IconButton>
              </Box>
              
              {processing && (
                <Box sx={{ mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                    Processing PDF...
                  </Typography>
                </Box>
              )}

              {!processing && (
                <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    onClick={handleUpload}
                    startIcon={<UploadIcon />}
                  >
                    Process PDF
                  </Button>
                  <Button variant="outlined" onClick={handleReset}>
                    Cancel
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        )}

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {result && (
          <Box sx={{ mt: 3 }}>
            {result.is_duplicate ? (
              <Alert
                severity="warning"
                icon={<WarningIcon />}
                sx={{ mb: 2 }}
              >
                This PDF has already been processed
              </Alert>
            ) : (
              <Alert
                severity="success"
                icon={<SuccessIcon />}
                sx={{ mb: 2 }}
              >
                PDF processed successfully!
              </Alert>
            )}

            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Processing Result
                </Typography>
                <Divider sx={{ my: 2 }} />
                
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Submission ID"
                      secondary={result.submission_id || 'N/A'}
                    />
                  </ListItem>
                  
                  {result.data && (
                    <>
                      <ListItem>
                        <ListItemText
                          primary="Project ID"
                          secondary={result.data.metadata?.project_id || 'N/A'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Total Samples"
                          secondary={result.data.total_samples || 0}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Owner"
                          secondary={result.data.metadata?.owner || 'N/A'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText
                          primary="Source Organism"
                          secondary={result.data.metadata?.source_organism || 'N/A'}
                        />
                      </ListItem>
                    </>
                  )}
                  
                  <ListItem>
                    <ListItemText
                      primary="Status"
                      secondary={
                        <Chip
                          label={result.is_duplicate ? 'Duplicate' : 'New Submission'}
                          color={result.is_duplicate ? 'warning' : 'success'}
                          size="small"
                        />
                      }
                    />
                  </ListItem>
                </List>

                <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                  {!result.is_duplicate && (
                    <Button
                      variant="contained"
                      onClick={handleViewSubmission}
                    >
                      View Submission
                    </Button>
                  )}
                  <Button
                    variant="outlined"
                    onClick={handleReset}
                  >
                    Upload Another
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Box>
        )}
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Upload Guidelines
        </Typography>
        <List>
          <ListItem>
            <ListItemText
              primary="File Format"
              secondary="Only PDF files are accepted (HTSF Nanopore submission forms)"
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Duplicate Detection"
              secondary="The system automatically detects if a PDF has been processed before"
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Data Extraction"
              secondary="Sample data, project information, and metadata are automatically extracted"
            />
          </ListItem>
          <ListItem>
            <ListItemText
              primary="Storage"
              secondary="All submissions are stored in the database with unique identifiers"
            />
          </ListItem>
        </List>
      </Paper>
    </Box>
  );
}

export default Upload;
