const Card = ({ children, className }) => (
    <div className={`rounded-xl shadow-lg ${className}`}>{children}</div>
);
  
const CardHeader = ({ children, className }) => (
    <div className={`p-4 border-b border-gray-700 ${className}`}>{children}</div>
);
  
const CardTitle = ({ children, className }) => (
    <h2 className={`text-xl font-bold text-white ${className}`}>{children}</h2>
);
  
const CardContent = ({ children, className }) => (
    <div className={`p-4 ${className}`}>{children}</div>
);

export { Card, CardHeader, CardTitle, CardContent };