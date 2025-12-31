/**
 * Cloudflare Worker for Japan Postal Code API
 * Reads grouped JSON files from GitHub Pages to find postal codes matching the input prefix
 */

const DATA_BASE_URL = 'https://stayforge.github.io/japan-postal-code/datasets';

const jsonCache = new Map();
const CACHE_TTL = 3600000; // 1 hour

async function loadJson(url) {
  const cached = jsonCache.get(url);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  try {
    const response = await fetch(url);
    if (!response.ok) return null;
    
    const data = await response.json();
    jsonCache.set(url, { data, timestamp: Date.now() });
    return data;
  } catch (error) {
    console.error(`Error loading ${url}:`, error);
    return null;
  }
}

function filterByPrefix(data, prefix) {
  if (!Array.isArray(data)) data = [data];
  return data.filter(item => (item.postal_code || '').startsWith(prefix));
}

export default {
  async fetch(request) {
    if (request.method !== 'GET') {
      return new Response(
        JSON.stringify({ error: 'Method not allowed' }),
        { status: 405, headers: { 'Content-Type': 'application/json' } }
      );
    }

    try {
      const url = new URL(request.url);
      let postalCode = url.searchParams.get('code') || 
                       url.searchParams.get('postal_code') || 
                       url.searchParams.get('q') ||
                       url.pathname.match(/\/([0-9-]+)$/)?.[1];

      if (!postalCode) {
        return new Response(
          JSON.stringify({ error: 'Postal code parameter is required' }),
          { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
      }

      const digitsOnly = postalCode.replace(/\D/g, '');

      if (digitsOnly.length < 3) {
        return new Response(
          JSON.stringify({ error: 'Postal code must be at least 3 digits' }),
          { status: 400, headers: { 'Content-Type': 'application/json' } }
        );
      }

      const prefix = digitsOnly.substring(0, 3);
      let results = [];

      if (digitsOnly.length === 7) {
        const suffix = digitsOnly.substring(3);
        const suffixData = await loadJson(`${DATA_BASE_URL}/${prefix}/${suffix}.json`);
        if (suffixData) {
          results = Array.isArray(suffixData) ? suffixData : [suffixData];
        } else {
          const prefixData = await loadJson(`${DATA_BASE_URL}/${prefix}.json`);
          if (prefixData) results = filterByPrefix(prefixData, digitsOnly);
        }
      } else {
        const prefixData = await loadJson(`${DATA_BASE_URL}/${prefix}.json`);
        if (prefixData) results = filterByPrefix(prefixData, digitsOnly);
      }

      results.sort((a, b) => (a.postal_code || '').localeCompare(b.postal_code || ''));
      if (results.length > 1000) results = results.slice(0, 1000);

      return new Response(
        JSON.stringify({
          query: postalCode,
          extracted_digits: digitsOnly,
          count: results.length,
          results
        }, null, 2),
        {
          status: 200,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        }
      );
    } catch (error) {
      return new Response(
        JSON.stringify({ error: 'Internal server error', message: error.message }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }
  },
};

