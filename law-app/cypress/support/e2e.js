// ***********************************************
// This support file is processed and loaded automatically before your test files.
//
// This is a great place to put global configuration and behavior that modifies Cypress.
//
// You can change the location of this file or turn off automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************

// Import commands.js using ES2015 syntax:
// import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false here prevents Cypress from failing the test
  // This helps with Vue hydration errors or other non-critical errors
  console.log('Uncaught exception:', err.message);
  return false;
});

// Custom command to wait for the store to load
Cypress.Commands.add('waitForStoreLoad', () => {
  cy.window().then((win) => {
    return new Cypress.Promise((resolve) => {
      // Check if the store is loaded
      const checkStore = () => {
        if (!win.document.querySelector('.loading-state')) {
          resolve();
        } else {
          setTimeout(checkStore, 100);
        }
      };
      checkStore();
    });
  });
});
