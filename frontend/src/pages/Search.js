import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Chip,
  Grid,
  InputAdornment,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Search as SearchIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import apiService from '../services/api';

function Search() {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      setError('Please enter a search term');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await apiService.search(searchQuery);
      setResults(response.data);
    } catch (err) {
      setError('Failed to perform search');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setSearchQuery('');
    setResults(null);
    setError(null);
  };

  const handleViewSubmission = (submissionId) => {
    navigate(`/submissions/${submissionId}`);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Search Submissions
      </Typography>
      <Typography variant="body1" color="textSecondary" paragraph>
        Search across all submission fields including project IDs, owners, and metadata
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <form onSubmit={handleSearch}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={9}>
              <TextField
                fullWidth
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter search term (e.g., project ID, owner name, organism...)"
                variant="outlined"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                  endAdornment: searchQuery && (
                    <InputAdornment position="end">
                      <ClearIcon
                        sx={{ cursor: 'pointer' }}
                        onClick={handleClear}
                      />
                    </InputAdornment>
                  ),
                }}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                size="large"
                disabled={loading || !searchQuery.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
              >
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </Grid>
          </Grid>
        </form>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
      </Paper>

      {results && (
        <Paper sx={{ p: 3 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Search Results
            </Typography>
            <Chip
              label={`${results.count} result${results.count !== 1 ? 's' : ''} found`}
              color="primary"
              variant="outlined"
            />
          </Box>

          {results.count === 0 ? (
            <Alert severity="info">
              No submissions found matching "{searchQuery}"
            </Alert>
          ) : (
            <Grid container spacing={2}>
              {results.results.map((submission) => (
                <Grid item xs={12} key={submission.submission_id}>
                  <Card
                    sx={{
                      cursor: 'pointer',
                      '&:hover': {
                        boxShadow: 3,
                        bgcolor: 'action.hover',
                      },
                      transition: 'all 0.3s',
                    }}
                    onClick={() => handleViewSubmission(submission.submission_id)}
                  >
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="start">
                        <Box flex={1}>
                          <Typography variant="h6" gutterBottom>
                            {submission.submission_id}
                          </Typography>
                          
                          <List dense disablePadding>
                            <ListItem disablePadding>
                              <ListItemText
                                primary="Project"
                                secondary={submission.project_id || 'N/A'}
                              />
                            </ListItem>
                            <ListItem disablePadding>
                              <ListItemText
                                primary="Owner"
                                secondary={submission.owner || 'N/A'}
                              />
                            </ListItem>
                            <ListItem disablePadding>
                              <ListItemText
                                primary="File"
                                secondary={submission.pdf_filename || 'N/A'}
                              />
                            </ListItem>
                          </List>
                        </Box>
                        
                        <Box textAlign="right">
                          <Chip
                            label={submission.short_ref}
                            size="small"
                            color="primary"
                            variant="outlined"
                            sx={{ mb: 1 }}
                          />
                          <Typography variant="body2" color="textSecondary">
                            {submission.total_samples} samples
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {new Date(submission.scanned_at).toLocaleDateString()}
                          </Typography>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </Paper>
      )}

      {!results && !loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <SearchIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="textSecondary" gutterBottom>
            Start Searching
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Enter a search term above to find submissions
          </Typography>
        </Paper>
      )}
    </Box>
  );
}

export default Search;
