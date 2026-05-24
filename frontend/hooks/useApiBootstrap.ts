"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ApiError,
  fetchHealth,
  fetchLocations,
  fetchMetadata,
} from "@/lib/api/client";
import { missingApiConfigMessage } from "@/lib/api/config";
import type { MetadataResponse } from "@/lib/api/types";

const DATA_POLL_MS = 3000;
const DATA_POLL_MAX = 40;

export function useApiBootstrap() {
  const [locations, setLocations] = useState<string[]>([]);
  const [metadata, setMetadata] = useState<MetadataResponse | null>(null);
  const [bootstrapping, setBootstrapping] = useState(true);
  const [dataLoading, setDataLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const loadCatalog = useCallback(async () => {
    const [locRes, metaRes] = await Promise.all([
      fetchLocations(),
      fetchMetadata(),
    ]);
    setLocations(locRes.locations);
    setMetadata(metaRes);
    setLoadError(null);
    setDataLoading(false);
  }, []);

  useEffect(() => {
    const configError = missingApiConfigMessage();
    if (configError) {
      setLoadError(configError);
      setBootstrapping(false);
      return;
    }

    let cancelled = false;
    let pollTimer: ReturnType<typeof setTimeout> | undefined;
    let attempts = 0;

    const waitForData = async (): Promise<boolean> => {
      while (attempts < DATA_POLL_MAX && !cancelled) {
        attempts += 1;
        try {
          const health = await fetchHealth();
          if (health.data_loaded) return true;
        } catch {
          return false;
        }
        setDataLoading(true);
        await new Promise((resolve) => {
          pollTimer = setTimeout(resolve, DATA_POLL_MS);
        });
      }
      return false;
    };

    (async () => {
      try {
        const health = await fetchHealth();
        if (!health.data_loaded) {
          setDataLoading(true);
          const ready = await waitForData();
          if (cancelled) return;
          if (!ready) {
            setLoadError(
              "Restaurant data is still loading on the server. Wait a minute and refresh, or check Railway logs.",
            );
            setBootstrapping(false);
            return;
          }
        }
        await loadCatalog();
      } catch (err) {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 503) {
          setDataLoading(true);
          const ready = await waitForData();
          if (cancelled) return;
          if (ready) {
            try {
              await loadCatalog();
              if (!cancelled) setBootstrapping(false);
              return;
            } catch (inner) {
              err = inner;
            }
          }
        }
        const message =
          err instanceof ApiError
            ? err.message
            : isConnectionError(err)
              ? connectionErrorMessage()
              : "Could not connect to the API.";
        setLoadError(message);
      } finally {
        if (!cancelled) setBootstrapping(false);
      }
    })();

    return () => {
      cancelled = true;
      if (pollTimer) clearTimeout(pollTimer);
    };
  }, [loadCatalog]);

  return {
    locations,
    metadata,
    bootstrapping,
    dataLoading,
    loadError,
    dataReady: locations.length > 0,
  };
}

function isConnectionError(err: unknown): boolean {
  return err instanceof TypeError;
}

function connectionErrorMessage(): string {
  if (process.env.NEXT_PUBLIC_API_BASE_URL) {
    return (
      "Cannot reach the API. Check NEXT_PUBLIC_API_BASE_URL, Railway is running, " +
      "and CORS_ORIGINS on Railway includes this Vercel URL."
    );
  }
  return "Cannot reach the API. Run `zm api` locally, or set NEXT_PUBLIC_API_BASE_URL on Vercel.";
}
