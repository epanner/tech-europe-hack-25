import { useState } from 'react';

interface BreachPredictionRequest {
  case_description: string;
  lawfulness_of_processing: string;
  data_subject_rights_compliance: string;
  risk_management_and_safeguards: string;
  accountability_and_governance: string;
}

interface SimilarCase {
  id: string;
  company: string;
  description: string;
  fine: number;
  similarity: number;
  explanation_of_similarity: string;
  date: string;
  authority: string;
}

interface PredictionResult {
  predicted_fine: number;
  explanation_for_fine: string;
}

interface BreachPredictionResponse {
  similar_cases: SimilarCase[];
  prediction_result: PredictionResult;
  error?: string;
}

export const useBreachPrediction = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<BreachPredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const predictBreachImpact = async (request: BreachPredictionRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://127.0.0.1:5000/api/predict-breach-impact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to predict breach impact');
      }

      const result: BreachPredictionResponse = await response.json();
      setData(result);
      
      if (result.error) {
        setError(result.error);
      }
      
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    predictBreachImpact,
    loading,
    data,
    error,
    reset: () => {
      setData(null);
      setError(null);
    }
  };
};

export default useBreachPrediction;
