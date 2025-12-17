export interface ItemCode {
  code: string;
  location?: string;
}

export interface PendantDescription {
  itemCode: string;
  title: string;
  visualDescription: string;
  symbolism: string;
  poeticCopy: string;
}

export enum AppState {
  IDLE = 'IDLE',
  ANALYZING_CODES = 'ANALYZING_CODES',
  SELECTING_ITEM = 'SELECTING_ITEM',
  GENERATING_DESCRIPTION = 'GENERATING_DESCRIPTION',
  VIEWING_RESULT = 'VIEWING_RESULT',
  ERROR = 'ERROR'
}

export interface AnalysisError {
  message: string;
}
