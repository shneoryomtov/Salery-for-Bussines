import { NextRequest, NextResponse } from 'next/server';
import { calculateAll, DEFAULT_TAX_SETTINGS } from '@/lib/calculator';
import { ScenarioInput } from '@/lib/types';

export async function POST(request: NextRequest) {
  try {
    const scenario: ScenarioInput = await request.json();
    const results = calculateAll(scenario, DEFAULT_TAX_SETTINGS);
    return NextResponse.json(results);
  } catch (error) {
    console.error('Calculation error:', error);
    return NextResponse.json(
      { error: 'Failed to calculate' },
      { status: 400 }
    );
  }
}
