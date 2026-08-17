import { useState, useEffect } from 'react';

export const useConnection = () => {
  const [connectionData, setConnectionData] = useState({
    isOnline: false,
    queueSize: 0
  });

  useEffect(() => {
    const checkStatus = async () => {
      try {
        // Interroge l'endpoint /health ou /connection-status de votre FastAPI
        const response = await fetch('/health'); 
        if (response.ok) {
          const data = await response.json();
          // Le backend renvoie "connection": "offline" ou "online"
          const online = data.connection === 'online';
          setConnectionData({
            isOnline: online,
            queueSize: data.sync_queue || 0
          });
        } else {
          setConnectionData(prev => ({ ...prev, isOnline: false }));
        }
      } catch (error) {
        setConnectionData(prev => ({ ...prev, isOnline: false }));
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 4000); // Vérifie toutes les 4 secondes

    return () => clearInterval(interval);
  }, []);

  return connectionData;
};