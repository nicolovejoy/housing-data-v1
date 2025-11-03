/**
 * Database schema definitions for FMR data
 * Run migrations to create these tables in PostgreSQL
 */

export const schema = {
  tables: {
    areas: {
      description: 'Geographic areas (metros and counties)',
      columns: {
        id: 'UUID PRIMARY KEY DEFAULT gen_random_uuid()',
        name: 'VARCHAR(255) NOT NULL',
        type: "VARCHAR(20) CHECK (type IN ('metro', 'county'))",
        state: 'VARCHAR(2) NOT NULL',
        state_name: 'VARCHAR(100)',
        created_at: 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
      },
      indexes: ['(state)', '(type)', '(name)'],
    },
    rents: {
      description: 'Rent data for each area',
      columns: {
        id: 'UUID PRIMARY KEY DEFAULT gen_random_uuid()',
        area_id: 'UUID NOT NULL REFERENCES areas(id) ON DELETE CASCADE',
        studio_rent: 'INTEGER',
        one_bedroom_rent: 'INTEGER',
        two_bedroom_rent: 'INTEGER',
        three_bedroom_rent: 'INTEGER',
        four_bedroom_rent: 'INTEGER',
        created_at: 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
      },
      indexes: ['(area_id)', '(two_bedroom_rent)'],
    },
  },
};

export type Schema = typeof schema;
