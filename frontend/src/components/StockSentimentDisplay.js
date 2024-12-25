import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, Newspaper } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './card';

const SentimentBadge = ({ prediction }) => {
  if (prediction === null || prediction === undefined) {
    return null;
  }

  const getSentimentClass = (score) => {
    if (score <= 40) return 'bg-red-100 text-red-800';
    if (score >= 60) return 'bg-green-100 text-green-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  const getSentimentText = (score) => {
    if (score <= 40) return 'Bearish';
    if (score >= 60) return 'Bullish';
    return 'Neutral';
  };

  const getSentimentIcon = (score) => {
    if (score <= 40) return <TrendingDown className="h-4 w-4 mr-1" />;
    if (score >= 60) return <TrendingUp className="h-4 w-4 mr-1" />;
    return <AlertTriangle className="h-4 w-4 mr-1" />;
  };

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getSentimentClass(prediction)}`}>
      {getSentimentIcon(prediction)}
      {getSentimentText(prediction)} ({prediction.toFixed(1)})
    </div>
  );
};

const NewsSection = ({ title, news, icon: Icon }) => {
    const newsToRender = news || [];
    
    if (newsToRender.length === 0) return null;
  
    return (
      <div className="bg-gray-800 rounded-xl p-6 shadow-lg col-span-2">
        <h2 className="text-xl font-bold mb-4 flex items-center">
          <Icon className="h-6 w-6 mr-2" />
          <span>{title}</span>
        </h2>
        <div className="space-y-6">
          {newsToRender.map((article, index) => (
            <div key={index} className="border-b border-gray-700 last:border-b-0 pb-6">
              {article.url ? (
                <a 
                  href={article.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="group block cursor-pointer"
                >
                  <h3 className="font-medium text-lg mb-2 group-hover:text-blue-400 transition-colors">
                    {article.headline || "No headline available"}
                  </h3>
                  {article.description && (
                    <p className="text-gray-400 mb-3 text-sm leading-relaxed">
                      {article.description}
                    </p>
                  )}
                </a>
              ) : (
                <div>
                  <h3 className="font-medium text-lg mb-2">
                    {article.headline || "No headline available"}
                  </h3>
                  <p className="text-gray-400 mb-3 text-sm leading-relaxed">
                    {article.description || "No description available."}
                  </p>
                  <span className="text-gray-400">Link not available</span>
                </div>
              )}
              <div className="flex justify-between items-center">
            <div className="text-sm text-gray-400">
                {article.publisher && (
                <>
                    {article.publisher}
                    {article.published_at && ` - ${new Date(article.published_at).toLocaleDateString()}`}
                </>
                )}
                {article.published_at && !article.publisher && (
                <>
                    {new Date(article.published_at).toLocaleDateString()}
                </>
                )}
            </div>
            {article.relevant_prediction && (
                <SentimentBadge prediction={article.relevant_prediction} />
            )}
            </div>
            </div>
          ))}
        </div>
      </div>
    );
  };
  
const StockSentimentDisplay = ({ stockDetails }) => {
  return (
    <>

      {/* News Sections */}
      <div className="grid grid-cols-1 gap-6">
        <NewsSection 
          title={`${stockDetails.profile.name} News`}
          news={stockDetails.news} 
          icon={Newspaper}
        />

        {stockDetails.country_news && stockDetails.country_news.length > 0 && (
          <NewsSection 
            title={`${stockDetails.profile.country} Market News`}
            news={stockDetails.country_news}
            icon={Newspaper}
          />
        )}
      </div>
    </>
  );
};

export default StockSentimentDisplay;