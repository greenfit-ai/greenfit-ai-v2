import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, CodeXml, Database, Sprout } from 'lucide-react';
import { Button } from '@/components/ui/button';

export const Landing: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 pt-20 pb-16">
        <div className="text-center max-w-3xl mx-auto">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-yellow-400 to-green-600 bg-clip-text text-transparent">
            Welcome to GreenFit AI!
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Your everyday companion to help you make more sustainability-informed choices when purchasing
          </p>
          <Button 
            onClick={() => navigate('/chat')}
            className="bg-green-600 hover:bg-green-700 text-white px-8 py-6 rounded-lg text-lg font-semibold transition-all hover:scale-105"
          >
            Start Discovering Now
            <ArrowRight className="ml-2" />
          </Button>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Sprout className="text-green-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Reliable Sustainability</h3>
            <p className="text-gray-600">
                Discover the environmental impact of sports clothing, in a easy and reliable way
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="bg-amber-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <CodeXml className="text-amber-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">AI Powered</h3>
            <p className="text-gray-600">
                AI handles your searches, evaluates product sustainability and creates summaries for you!
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <div className="bg-lime-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Database className="text-lime-600" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Data-driven and data-centered</h3>
            <p className="text-gray-600">
                We accurately selected data for RAG and are continuously updating them! We're backed by <a href='https://qdrant.tech' className="text-lime-700 underline">Qdrant</a>.
            </p>
          </div>
        </div>
      </div>

      {/* Social Proof Section */}
      <div className="bg-green-30 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-2xl mx-auto">
            <h2 className="text-3xl font-bold mb-8 bg-gradient-to-r from-yellow-400 to-green-600 bg-clip-text text-transparent">Created for Everyone</h2>
            <div className="grid grid-cols-3 gap-8 text-center">
              <div>
                <p className="text-4xl font-bold text-green-600 mb-2">20+</p>
                <p className="text-gray-600">Scientific sources</p>
              </div>
              <div>
                <p className="text-4xl font-bold text-amber-500 mb-2">3</p>
                <p className="text-gray-600">Evaluation metrics</p>
              </div>
              <div>
                <p className="text-4xl font-bold text-lime-500 mb-2">Easy</p>
                <p className="text-gray-600">To use for everyone</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-4 py-16 text-center">
        <h2 className="text-3xl font-bold mb-6 bg-gradient-to-r from-yellow-400 to-green-600 bg-clip-text text-transparent">Ready to find out the sustainability of your sport products?</h2>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Let GreenFit AI guide you and suggest you the most eco-friendly purchases!
        </p>
        <Button 
          onClick={() => navigate('/chat')}
          className="bg-gradient-to-r from-lime-400 to-green-600 hover:from-lime-500 hover:to-green-700 text-white px-8 py-6 rounded-lg text-lg font-semibold transition-all hover:scale-105"
        >
          Begin Your Journey
          <ArrowRight className="ml-2" />
        </Button>
      </div>
    </div>
  );
};