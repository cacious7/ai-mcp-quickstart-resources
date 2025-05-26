/// <reference types="cypress" />

describe('Laws Page', () => {
  beforeEach(() => {
    // Visit the laws page
    cy.visit('/laws');
    
    // Wait for store to load
    cy.waitForStoreLoad();
  });

  it('displays the page title and search bar', () => {
    cy.contains('Zambian Laws & Regulations').should('be.visible');
    cy.get('input[placeholder="Search laws, acts, regulations..."]').should('be.visible');
  });

  it('shows a list of laws', () => {
    // Wait for loading state to finish if present
    cy.get('.loading-state').should('not.exist', { timeout: 5000 });
    // Check for law cards or no results
    cy.get('body').then(($body) => {
      if ($body.find('.law-card').length > 0) {
        cy.get('.law-card').should('exist');
      } else if ($body.find('.no-results').length > 0) {
        cy.log('No laws found in the initial state');
        cy.get('.no-results').should('be.visible');
      }
    });
  });

  it('filters by category', () => {
    // Wait for categories to load
    cy.get('select#category').should('exist');
    cy.get('select#category option').then(options => {
      if (options.length > 1) {
        cy.get('select#category').select(1);
        cy.get('.loading-state').should('not.exist', { timeout: 5000 });
      } else {
        cy.log('No categories available for filtering');
      }
    });
  });

  it('searches for a law', () => {
    cy.get('input[placeholder="Search laws, acts, regulations..."]').type('Law');
    cy.get('.search-btn').click();
    // Allow time for search results
    cy.wait(1000);
  });

  it('clears filters', () => {
    // First apply a filter
    cy.get('select#type').then($select => {
      if ($select.find('option').length > 1) {
        cy.wrap($select).select(1);
      }
    });
    // Then clear filters
    cy.get('.clear-filters-btn').click();
    cy.wait(1000);
  });
  
  // Conditionally test pagination only if there are enough results
  it('tests pagination if available', () => {
    cy.get('body').then($body => {
      if ($body.find('.pagination-btn').length > 0) {
        cy.get('.pagination-btn').contains('Next').click({force: true});
        cy.wait(500);
      } else {
        cy.log('Pagination not available - not enough results');
      }
    });
  });

  // Conditionally test AI chat button if any law cards exist
  it('tests Ask AI chat if laws exist', () => {
    cy.get('body').then($body => {
      if ($body.find('.law-card').length > 0) {
        cy.get('.law-card').first().find('.btn').contains('Ask AI').click({force: true});
        cy.url().should('include', '/chat');
      } else {
        cy.log('No law cards available to test Ask AI button');
      }
    });
  });
});
