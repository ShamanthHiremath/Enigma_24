import React from 'react';
import { AlertOctagon, Info, CheckCircle, AlertTriangle } from 'lucide-react';

const Alert = ({ variant = 'info', children, className = '' }) => {
  const getAlertStyles = () => {
    switch (variant) {
      case 'destructive':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'success':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-300';
    }
  };

  const getIcon = () => {
    switch (variant) {
      case 'destructive':
        return <AlertOctagon className="w-5 h-5 mr-2" />;
      case 'success':
        return <CheckCircle className="w-5 h-5 mr-2" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 mr-2" />;
      default:
        return <Info className="w-5 h-5 mr-2" />;
    }
  };

  return (
    <div
      className={`flex items-center p-4 border-l-4 rounded-md ${getAlertStyles()} ${className}`}
    >
      {getIcon()}
      <div>{children}</div>
    </div>
  );
};

const AlertDescription = ({ children }) => {
    return <p className="text-sm leading-relaxed">{children}</p>;
};
export { Alert, AlertDescription };
  