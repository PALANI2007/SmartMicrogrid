import React, { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * ErrorBoundary: React class component that catches uncaught errors in the
 * component subtree and displays a user-friendly recovery UI instead of
 * crashing the entire application.
 *
 * Usage: Wrap any page or component subtree:
 *   <ErrorBoundary>
 *     <MyPage />
 *   </ErrorBoundary>
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error details without exposing secrets or internal paths
    console.error('[ErrorBoundary] Component error caught:', error.message);
    console.error('[ErrorBoundary] Component stack:', errorInfo.componentStack);
    this.setState({ errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="card border border-red-700/50 bg-red-900/10 p-8 text-center space-y-4">
          <div className="text-4xl">&#x26A0;&#xFE0F;</div>
          <h2 className="text-xl font-semibold text-red-300">Something went wrong</h2>
          <p className="text-slate-400 text-sm max-w-md mx-auto">
            An unexpected error occurred in this section. The rest of the application
            remains functional.
          </p>
          {this.state.error && (
            <p className="text-xs text-slate-500 font-mono bg-slate-900 rounded-lg p-3 text-left max-w-lg mx-auto">
              {this.state.error.message}
            </p>
          )}
          <div className="flex gap-3 justify-center">
            <button
              onClick={this.handleReset}
              className="btn-primary"
            >
              Try Again
            </button>
            <button
              onClick={() => window.location.reload()}
              className="btn-secondary"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
