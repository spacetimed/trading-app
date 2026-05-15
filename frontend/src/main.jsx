import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createTheme, CssBaseline, ThemeProvider } from '@mui/material'
import './index.css'
import App from './App.jsx'

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#000',
      paper: '#09090b',
    },
    divider: '#27272a',
    primary: {
      main: '#e5e7eb',
      contrastText: '#09090b',
    },
    success: {
      main: '#86efac',
    },
    error: {
      main: '#fca5a5',
    },
    text: {
      primary: '#e5e7eb',
      secondary: '#8b8b94',
    },
  },
  shape: {
    borderRadius: 8,
  },
  typography: {
    fontSize: 13,
    fontFamily: [
      'JetBrains Mono',
      'SFMono-Regular',
      'Cascadia Code',
      'Consolas',
      'monospace',
    ].join(','),
    button: {
      fontSize: '0.78rem',
      fontWeight: 600,
      textTransform: 'none',
    },
    h5: {
      fontSize: '1.12rem',
      fontWeight: 700,
    },
    h6: {
      fontSize: '0.9rem',
      fontWeight: 700,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
        },
        text: {
          color: '#a1a1aa',
          paddingInline: 0,
          '&:hover': {
            background: 'transparent',
            color: '#e5e7eb',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiCard: {
      defaultProps: {
        variant: 'outlined',
      },
      styleOverrides: {
        root: {
          borderColor: '#27272a',
          backgroundImage: 'none',
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: 18,
          '&:last-child': {
            paddingBottom: 18,
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderColor: '#27272a',
          fontSize: '0.78rem',
          paddingBlock: 10,
        },
        head: {
          color: '#8b8b94',
          fontSize: '0.7rem',
          fontWeight: 700,
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
      },
    },
  },
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </StrictMode>,
)
