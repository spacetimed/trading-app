import { useCallback, useEffect, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  ButtonGroup,
  Card,
  CardContent,
  Chip,
  Container,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material'

import {
  buyOrder,
  depositAccount,
  getAccountSummary,
  getCurrentUser,
  getPortfolio,
  getQuote,
  getTrades,
  loginUser,
  registerUser,
  sellOrder,
  withdrawAccount,
} from './api'

const actionButtonSx = {
  bgcolor: '#141416',
  border: 1,
  borderColor: 'divider',
  boxShadow: 'none',
  color: 'text.primary',
  '&:hover': {
    bgcolor: '#1f1f23',
    boxShadow: 'none',
  },
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('token') ?? '')
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('user@example.com')
  const [password, setPassword] = useState('testtest')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [summary, setSummary] = useState(null)
  const [portfolio, setPortfolio] = useState([])
  const [trades, setTrades] = useState([])
  const [user, setUser] = useState(null)
  const [dashboardError, setDashboardError] = useState('')
  const [isDashboardLoading, setIsDashboardLoading] = useState(false)
  const [accountAction, setAccountAction] = useState('deposit')
  const [accountAmount, setAccountAmount] = useState('')
  const [accountMessage, setAccountMessage] = useState('')
  const [accountError, setAccountError] = useState('')
  const [isAccountSubmitting, setIsAccountSubmitting] = useState(false)
  const [quoteSymbol, setQuoteSymbol] = useState('AAPL')
  const [quote, setQuote] = useState(null)
  const [quoteError, setQuoteError] = useState('')
  const [isQuoteLoading, setIsQuoteLoading] = useState(false)
  const [orderSide, setOrderSide] = useState('buy')
  const [orderSymbol, setOrderSymbol] = useState('AAPL')
  const [orderQuantity, setOrderQuantity] = useState(1)
  const [orderMessage, setOrderMessage] = useState('')
  const [orderError, setOrderError] = useState('')
  const [isOrderSubmitting, setIsOrderSubmitting] = useState(false)

  const loadDashboard = useCallback(async () => {
    setDashboardError('')
    setIsDashboardLoading(true)

    try {
      const [summaryData, portfolioData, tradesData, userData] = await Promise.all([
        getAccountSummary(token),
        getPortfolio(token),
        getTrades(token),
        getCurrentUser(token),
      ])
      setSummary(summaryData)
      setPortfolio(portfolioData)
      setTrades(tradesData)
      setUser(userData)
    } catch (err) {
      setDashboardError(err.message)
    } finally {
      setIsDashboardLoading(false)
    }
  }, [token])

  useEffect(() => {
    if (token) {
      queueMicrotask(loadDashboard)
    }
  }, [token, loadDashboard])

  async function handleSubmit(event) {
    event.preventDefault()
    setMessage('')
    setError('')
    setIsSubmitting(true)

    try {
      if (mode === 'login') {
        const data = await loginUser({ email, password })
        localStorage.setItem('token', data.token)
        setMessage('login successful, redirecting...')
        setTimeout(() => setToken(data.token), 450)
      } else {
        const data = await registerUser({ email, password })
        setMessage(`registered ${data.email}. you can log in now.`)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleQuoteSubmit(event) {
    event.preventDefault()
    setQuote(null)
    setQuoteError('')
    setIsQuoteLoading(true)

    try {
      const symbol = quoteSymbol.trim().toUpperCase()
      if (!symbol) {
        throw new Error('symbol is required')
      }
      const data = await getQuote(symbol)
      setQuoteSymbol(symbol)
      setQuote(data)
    } catch (err) {
      setQuoteError(err.message)
    } finally {
      setIsQuoteLoading(false)
    }
  }

  async function handleAccountSubmit(event) {
    event.preventDefault()
    setAccountMessage('')
    setAccountError('')
    setIsAccountSubmitting(true)

    try {
      if (!accountAmount) {
        throw new Error('amount is required')
      }
      const payload = { amount: accountAmount }
      const data = accountAction === 'deposit'
        ? await depositAccount(token, payload)
        : await withdrawAccount(token, payload)

      setAccountAmount('')
      setAccountMessage(
        `${accountAction} complete. cash balance: ${formatMoney(data.cash_balance)}`,
      )
      await loadDashboard()
    } catch (err) {
      setAccountError(err.message)
    } finally {
      setIsAccountSubmitting(false)
    }
  }

  async function handleOrderSubmit(event) {
    event.preventDefault()
    setOrderMessage('')
    setOrderError('')
    setIsOrderSubmitting(true)

    try {
      const symbol = orderSymbol.trim().toUpperCase()
      if (!symbol) {
        throw new Error('symbol is required')
      }
      const payload = {
        symbol,
        quantity: Math.max(1, Number(orderQuantity)),
      }
      const data = orderSide === 'buy'
        ? await buyOrder(token, payload)
        : await sellOrder(token, payload)

      setOrderSymbol(payload.symbol)
      setOrderMessage(
        `${data.side ?? orderSide} ${data.quantity} ${data.symbol} @ ${formatMoney(data.price)}`,
      )
      await loadDashboard()
    } catch (err) {
      setOrderError(err.message)
    } finally {
      setIsOrderSubmitting(false)
    }
  }

  function handleLogout() {
    localStorage.removeItem('token')
    setToken('')
    setSummary(null)
    setPortfolio([])
    setTrades([])
    setUser(null)
    setQuote(null)
    setDashboardError('')
  }

  if (token) {
    return (
      <Box component="main" sx={{ minHeight: '100vh', py: 4 }}>
        <Container maxWidth="lg">
          <Stack spacing={3}>
            <Box
              sx={{
                alignItems: 'start',
                display: 'flex',
                gap: 2,
                justifyContent: 'space-between',
                width: '100%',
              }}
            >
              <Box>
                <Eyebrow>paper trading</Eyebrow>
                <Typography variant="h5">dashboard</Typography>
              </Box>
              <Box
                sx={{
                  alignItems: 'flex-end',
                  display: 'flex',
                  flexDirection: 'column',
                  lineHeight: 1.1,
                  ml: 'auto',
                  textAlign: 'right',
                }}
              >
                <Typography color="text.secondary" component="div" variant="caption">
                  hello, {formatUserName(user?.email)}
                </Typography>
                <Box
                  sx={{
                    display: 'flex',
                    gap: 1.25,
                    justifyContent: 'flex-end',
                    mt: 0.5,
                  }}
                >
                  <HeaderAction onClick={loadDashboard} disabled={isDashboardLoading}>
                    [refresh]
                  </HeaderAction>
                  <HeaderAction onClick={handleLogout}>
                    [logout]
                  </HeaderAction>
                </Box>
              </Box>
            </Box>

            <Box
              sx={{
                display: 'grid',
                gap: 2,
                gridTemplateColumns: { xs: '1fr', md: '1.35fr 0.85fr' },
              }}
            >
              <Stack spacing={2}>
                <Card>
                  <CardContent>
                    <PanelHeader
                      title="account summary"
                    />

                    {dashboardError && (
                      <Alert severity="error">{dashboardError}</Alert>
                    )}
                    {!summary && !dashboardError && (
                      <Typography color="text.secondary" variant="body2">
                        loading account data...
                      </Typography>
                    )}
                    {summary && (
                      <Box
                        sx={{
                          display: 'grid',
                          gap: 1.5,
                          gridTemplateColumns: {
                            xs: '1fr 1fr',
                            sm: 'repeat(4, 1fr)',
                          },
                        }}
                      >
                        <Stat
                          label="cash"
                          value={formatMoney(summary.cash_balance)}
                        />
                        <Stat
                          label="deposits"
                          value={formatMoney(summary.total_deposits)}
                        />
                        <Stat
                          label="withdrawals"
                          value={formatMoney(summary.total_withdrawals)}
                        />
                        <Stat label="transactions" value={summary.transaction_count} />
                      </Box>
                    )}
                    {summary && (
                      <Stack
                        component="form"
                        onSubmit={handleAccountSubmit}
                        spacing={1.25}
                        sx={{ mt: 1.75 }}
                      >
                        <ButtonGroup fullWidth size="small" variant="outlined">
                          <Button
                            onClick={() => setAccountAction('deposit')}
                            type="button"
                            variant={accountAction === 'deposit' ? 'contained' : 'outlined'}
                          >
                            deposit
                          </Button>
                          <Button
                            onClick={() => setAccountAction('withdraw')}
                            type="button"
                            variant={accountAction === 'withdraw' ? 'contained' : 'outlined'}
                          >
                            withdraw
                          </Button>
                        </ButtonGroup>
                        <Box
                          sx={{
                            alignItems: 'end',
                            display: 'grid',
                            gap: 1.5,
                            gridTemplateColumns: { xs: '1fr', sm: '176px auto' },
                            justifyContent: 'start',
                          }}
                        >
                          <MoneyStepper
                            onChange={setAccountAmount}
                            value={accountAmount}
                          />
                          <Button
                            disabled={isAccountSubmitting || !accountAmount}
                            sx={actionButtonSx}
                            type="submit"
                            variant="contained"
                          >
                            {isAccountSubmitting ? 'saving...' : accountAction}
                          </Button>
                        </Box>
                        {accountMessage && (
                          <Alert severity="success">{accountMessage}</Alert>
                        )}
                        {accountError && (
                          <Alert severity="error">{accountError}</Alert>
                        )}
                      </Stack>
                    )}
                    {!summary && (
                      <Box sx={{ display: 'flex', mt: 1.25 }}>
                        <Button
                          disabled={isDashboardLoading}
                          onClick={loadDashboard}
                          size="small"
                          sx={{ minWidth: 0, px: 0 }}
                          variant="text"
                        >
                          refresh
                        </Button>
                      </Box>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardContent sx={{ pb: 2.5 }}>
                    <PanelHeader title="positions" />
                    {portfolio.length === 0 ? (
                      <Typography color="text.secondary" variant="body2">
                        no open positions yet.
                      </Typography>
                    ) : (
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>symbol</TableCell>
                              <TableCell>qty</TableCell>
                              <TableCell>avg</TableCell>
                              <TableCell>price</TableCell>
                              <TableCell>value</TableCell>
                              <TableCell>p/l</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {portfolio.map((position) => (
                              <TableRow key={position.symbol}>
                                <TableCell>{position.symbol}</TableCell>
                                <TableCell>{position.quantity}</TableCell>
                                <TableCell>{formatMoney(position.avg_cost)}</TableCell>
                                <TableCell>
                                  {formatMoney(position.current_price)}
                                </TableCell>
                                <TableCell>
                                  {formatMoney(position.market_value)}
                                </TableCell>
                                <TableCell>
                                  <Chip
                                    color={getPnLColor(
                                      position.unrealized_gain_loss,
                                    )}
                                    label={`${formatMoney(position.unrealized_gain_loss)} · ${formatPercent(position.unrealized_gain_loss_percent)}`}
                                    size="small"
                                    variant="outlined"
                                  />
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardContent sx={{ pb: 2.5 }}>
                    <PanelHeader title="trade history" />
                    {trades.length === 0 ? (
                      <Typography color="text.secondary" variant="body2">
                        no trades yet.
                      </Typography>
                    ) : (
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>side</TableCell>
                              <TableCell>symbol</TableCell>
                              <TableCell>qty</TableCell>
                              <TableCell>price</TableCell>
                              <TableCell>date</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {trades.map((trade) => (
                              <TableRow key={`${trade.created_at}-${trade.symbol}-${trade.side}`}>
                                <TableCell>{trade.side}</TableCell>
                                <TableCell>{trade.symbol}</TableCell>
                                <TableCell>{trade.quantity}</TableCell>
                                <TableCell>{formatMoney(trade.price)}</TableCell>
                                <TableCell>{formatDateTime(trade.created_at)}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </CardContent>
                </Card>
              </Stack>

              <Card sx={{ alignSelf: 'start' }}>
                <CardContent sx={{ p: 2.5 }}>
                  <Stack spacing={3.25}>
                    <Box>
                      <PanelHeader title="quote lookup" />
                      <Box
                        component="form"
                        onSubmit={handleQuoteSubmit}
                        sx={{
                          alignItems: 'center',
                          display: 'grid',
                          gap: 1.5,
                          gridTemplateColumns: '1fr auto',
                        }}
                      >
                        <TextField
                          fullWidth
                          label="symbol"
                          onChange={(event) => setQuoteSymbol(event.target.value)}
                          size="small"
                          value={quoteSymbol}
                        />
                        <Button
                          disabled={isQuoteLoading || !quoteSymbol.trim()}
                          type="submit"
                          variant="contained"
                        >
                          {isQuoteLoading ? 'loading...' : 'quote'}
                        </Button>
                      </Box>

                      {quote && (
                        <Box
                          sx={{
                            alignItems: 'center',
                            bgcolor: 'rgba(134, 239, 172, 0.07)',
                            border: 1,
                            borderColor: 'success.dark',
                            borderRadius: 1,
                            display: 'flex',
                            gap: 1.5,
                            justifyContent: 'flex-start',
                            mt: 2,
                            p: 2,
                          }}
                        >
                          <Chip color="success" label={quote.symbol} size="small" />
                          <Typography
                            color="success.main"
                            fontWeight={700}
                            sx={{ ml: 0.5 }}
                          >
                            {formatMoney(quote.price)}
                          </Typography>
                        </Box>
                      )}
                      {quoteError && (
                        <Alert severity="error" sx={{ mt: 2 }}>
                          {quoteError}
                        </Alert>
                      )}
                    </Box>

                    <Box component="form" onSubmit={handleOrderSubmit}>
                      <PanelHeader title="trade" />
                      <Stack spacing={1.5}>
                        <ButtonGroup fullWidth size="small" variant="outlined">
                          <Button
                            onClick={() => setOrderSide('buy')}
                            type="button"
                            variant={orderSide === 'buy' ? 'contained' : 'outlined'}
                          >
                            buy
                          </Button>
                          <Button
                            onClick={() => setOrderSide('sell')}
                            type="button"
                            variant={orderSide === 'sell' ? 'contained' : 'outlined'}
                          >
                            sell
                          </Button>
                        </ButtonGroup>
                        <Box
                          sx={{
                            alignItems: 'end',
                            display: 'grid',
                            gap: 1.5,
                            gridTemplateColumns: { xs: '1fr', sm: '1fr auto' },
                          }}
                        >
                          <TextField
                            fullWidth
                            label="symbol"
                            onChange={(event) => setOrderSymbol(event.target.value)}
                            size="small"
                            value={orderSymbol}
                          />
                          <QuantityStepper
                            onChange={setOrderQuantity}
                            value={orderQuantity}
                          />
                        </Box>
                        <Button
                          disabled={isOrderSubmitting || !orderSymbol.trim()}
                          sx={actionButtonSx}
                          type="submit"
                          variant="contained"
                        >
                          {isOrderSubmitting ? 'submitting...' : `${orderSide} shares`}
                        </Button>
                      </Stack>
                      {orderMessage && (
                        <Alert severity="success" sx={{ mt: 2 }}>
                          {orderMessage}
                        </Alert>
                      )}
                      {orderError && (
                        <Alert severity="error" sx={{ mt: 2 }}>
                          {orderError}
                        </Alert>
                      )}
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Box>
          </Stack>
        </Container>
      </Box>
    )
  }

  return (
    <Box
      component="main"
      sx={{
        display: 'grid',
        minHeight: '100vh',
        placeItems: 'center',
        px: 2,
      }}
    >
      <Card sx={{ maxWidth: 420, width: '100%' }}>
        <CardContent sx={{ p: 3.5 }}>
          <Stack spacing={2.25}>
            <Box>
              <Eyebrow>paper trading</Eyebrow>
              <Typography variant="h5">
                {mode === 'login' ? 'log in' : 'register'}
              </Typography>
              <Typography color="text.secondary" sx={{ mt: 1 }} variant="body2">
                connect to your local FastAPI backend.
              </Typography>
            </Box>

            <ButtonGroup fullWidth variant="outlined">
              <Button
                onClick={() => setMode('login')}
                variant={mode === 'login' ? 'contained' : 'outlined'}
              >
                login
              </Button>
              <Button
                onClick={() => setMode('register')}
                variant={mode === 'register' ? 'contained' : 'outlined'}
              >
                register
              </Button>
            </ButtonGroup>

            <Stack component="form" onSubmit={handleSubmit} spacing={2}>
              <TextField
                autoComplete="email"
                fullWidth
                label="email"
                onChange={(event) => setEmail(event.target.value)}
                type="email"
                value={email}
              />
              <TextField
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                fullWidth
                label="password"
                onChange={(event) => setPassword(event.target.value)}
                slotProps={{ htmlInput: { minLength: 8 } }}
                type="password"
                value={password}
              />
              <Button disabled={isSubmitting} type="submit" variant="contained">
                {isSubmitting ? 'working...' : mode}
              </Button>
            </Stack>

            {message && <Alert severity="success">{message}</Alert>}
            {error && <Alert severity="error">{error}</Alert>}
          </Stack>
        </CardContent>
      </Card>
    </Box>
  )
}

function Eyebrow({ children }) {
  return (
    <Typography
      color="text.secondary"
      fontWeight={700}
      sx={{ letterSpacing: '0.08em', textTransform: 'uppercase' }}
      variant="caption"
    >
      {children}
    </Typography>
  )
}

function PanelHeader({ title }) {
  return (
    <Typography
      color="text.secondary"
      component="div"
      fontWeight={700}
      sx={{ letterSpacing: '0.08em', mb: 1.5, textTransform: 'uppercase' }}
      variant="caption"
    >
      {title}
    </Typography>
  )
}

function HeaderAction({ children, disabled = false, onClick }) {
  return (
    <Button
      color="inherit"
      disabled={disabled}
      onClick={onClick}
      sx={{
        fontSize: '0.68rem',
        lineHeight: 1,
        minWidth: 0,
        p: 0,
      }}
      variant="text"
    >
      {children}
    </Button>
  )
}

function QuantityStepper({ onChange, value }) {
  const quantity = Math.max(1, Number(value) || 1)

  return (
    <Stack spacing={0.5} sx={{ width: { xs: '100%', sm: 144 } }}>
      <Typography color="text.secondary" variant="caption">
        qty
      </Typography>
      <ButtonGroup fullWidth size="small" variant="outlined">
        <Button onClick={() => onChange(Math.max(1, quantity - 1))} type="button">
          -
        </Button>
        <Button
          sx={{
            '&.Mui-disabled': {
              WebkitTextFillColor: '#e5e7eb',
              borderColor: 'divider',
              color: 'text.primary',
              opacity: 1,
            },
          }}
        >
          {quantity}
        </Button>
        <Button onClick={() => onChange(quantity + 1)} type="button">
          +
        </Button>
      </ButtonGroup>
    </Stack>
  )
}

function MoneyStepper({ onChange, value }) {
  const amount = Math.max(0, Number(value) || 0)

  function updateAmount(nextAmount) {
    onChange(nextAmount.toFixed(2))
  }

  return (
    <Stack spacing={0.5} sx={{ width: { xs: '100%', sm: 176 } }}>
      <Typography color="text.secondary" variant="caption">
        amount
      </Typography>
      <Box
        sx={{
          border: 1,
          borderColor: 'divider',
          borderRadius: 1,
          display: 'grid',
          gridTemplateColumns: '44px 1fr 44px',
          height: 35,
          overflow: 'hidden',
        }}
      >
        <Button
          onClick={() => updateAmount(Math.max(0, amount - 10))}
          sx={{ borderRadius: 0, minWidth: 0 }}
          type="button"
        >
          -
        </Button>
        <Box
          component="input"
          inputMode="decimal"
          onChange={(event) => onChange(event.target.value)}
          placeholder="0.00"
          sx={{
            bgcolor: 'transparent',
            border: 0,
            borderLeft: 1,
            borderRight: 1,
            borderColor: 'divider',
            color: 'text.primary',
            font: 'inherit',
            outline: 0,
            px: 1,
            textAlign: 'center',
            width: '100%',
          }}
          type="text"
          value={value}
        />
        <Button
          onClick={() => updateAmount(amount + 10)}
          sx={{ borderRadius: 0, minWidth: 0 }}
          type="button"
        >
          +
        </Button>
      </Box>
    </Stack>
  )
}

function Stat({ label, value }) {
  return (
    <Box
      sx={{
        bgcolor: 'background.default',
        border: 1,
        borderColor: 'divider',
        borderRadius: 1,
        minHeight: 92,
        p: 2,
      }}
    >
      <Typography color="text.secondary" variant="caption">
        {label}
      </Typography>
      <Typography
        color="text.primary"
        fontWeight={700}
        sx={{ mt: 1 }}
      >
        {value}
      </Typography>
    </Box>
  )
}

function formatUserName(email) {
  return email?.split('@')[0] ?? 'user'
}

function formatMoney(value) {
  return Number(value).toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
  })
}

function formatPercent(value) {
  return `${Number(value).toFixed(2)}%`
}

function formatDateTime(value) {
  return new Date(value).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function getPnLColor(value) {
  const amount = Number(value)

  if (amount > 0) {
    return 'success'
  }

  if (amount < 0) {
    return 'error'
  }

  return 'default'
}

export default App
