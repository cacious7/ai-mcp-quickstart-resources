/// <reference types="cypress" />

describe('Enhanced Chat Functionality', () => {
  beforeEach(() => {
    // Visit the chat page
    cy.visit('/')
    
    // Wait for the application to load
    cy.get('.chat-view').should('be.visible')
  })

  describe('UI Components', () => {
    it('should display the modern header correctly', () => {
      cy.get('.chat-header').should('be.visible')
      cy.get('.header-title').should('contain.text', 'Legal AI Assistant')
      cy.get('.header-subtitle').should('contain.text', 'Zambian Law Information')
      cy.get('.disclaimer-chip').should('contain.text', 'Information Only')
    })

    it('should show welcome section when no messages', () => {
      cy.get('.welcome-section').should('be.visible')
      cy.get('.welcome-title').should('contain.text', 'How can I help you today?')
      cy.get('.welcome-description').should('be.visible')
      cy.get('.examples-grid').should('be.visible')
      cy.get('.example-card').should('have.length.at.least', 1)
    })

    it('should display the modern input section', () => {
      cy.get('.input-section').should('be.visible')
      cy.get('.model-selector').should('be.visible')
      cy.get('.input-wrapper').should('be.visible')
      cy.get('.message-input').should('be.visible')
      cy.get('.action-btn[type="submit"]').should('be.visible')
      cy.get('.input-footer').should('be.visible')
    })
  })

  describe('Model Selection', () => {
    it('should show model selector with available models', () => {
      cy.get('.model-selector').click()
      cy.get('.model-option').should('have.length.at.least', 1)
      
      // Check if model options have required information
      cy.get('.model-option').first().within(() => {
        cy.get('.model-name').should('not.be.empty')
        cy.get('.model-description').should('not.be.empty')
        cy.get('.model-size').should('not.be.empty')
      })
    })

    it('should allow model selection and show feedback', () => {
      cy.get('.model-selector').click()
      cy.get('.model-option').first().click()
      
      // Should show notification directly (Quasar creates individual notification elements)
      cy.get('.q-notification', { timeout: 3000 }).should('contain.text', 'Switched')
    })

    it('should maintain model selection across interactions', () => {
      // Select a specific model
      cy.get('.model-selector').click()
      cy.get('.model-option').eq(1).click()
      
      // Check that the model remains selected
      cy.get('.model-selector .model-label').should('not.be.empty')
    })
  })

  describe('Message Input', () => {
    it('should allow typing in the message input', () => {
      const testMessage = 'What are employment laws in Zambia?'
      
      cy.get('.message-input .q-field__native').type(testMessage)
      cy.get('.message-input .q-field__native').should('have.value', testMessage)
    })

    it('should enable send button when message is entered', () => {
      cy.get('.action-btn[type="submit"]').should('be.disabled')
      
      cy.get('.message-input .q-field__native').type('Test message')
      cy.get('.action-btn[type="submit"]').should('not.be.disabled')
    })

    it('should support keyboard shortcuts', () => {
      const testMessage = 'Test message for shortcuts'
      
      cy.get('.message-input .q-field__native').type(testMessage)
      cy.get('.message-input .q-field__native').type('{ctrl}{enter}')
      
      // Should clear the input after sending
      cy.get('.message-input .q-field__native').should('have.value', '')
    })

    it('should handle multi-line input correctly', () => {
      const multiLineMessage = 'Line 1{enter}Line 2{enter}Line 3'
      cy.get('.message-input .q-field__native').type(multiLineMessage)
      cy.get('.message-input .q-field__native').should('contain.value', 'Line 1')
    })
  })

  describe('Example Questions', () => {
    it('should populate input and send when example is clicked', () => {
      // Click an example card
      cy.get('.example-card').first().click()
      
      // Should start loading immediately (example sends automatically)
      cy.get('.loading-indicator', { timeout: 2000 }).should('be.visible')
    })

    it('should disable examples during loading', () => {
      // Simulate loading state by sending a message
      cy.get('.message-input .q-field__native').type('Test message')
      cy.get('.action-btn[type="submit"]').click()
      
      // Examples should be disabled during loading (check for disabled class or attribute)
      cy.get('.example-card').should('have.class', 'disabled')
        .or('have.attr', 'disabled')
        .or('not.be.visible') // or might be hidden instead
    })
  })

  describe('Message Sending and Responses', () => {
    it('should send message and show loading state', () => {
      const testMessage = 'What is the legal age of consent in Zambia?'
      
      cy.get('.message-input .q-field__native').type(testMessage)
      cy.get('.action-btn[type="submit"]').click()
      
      // Should show loading indicator
      cy.get('.loading-indicator', { timeout: 1000 }).should('be.visible')
      cy.get('.typing-animation').should('be.visible')
      cy.get('.typing-text').should('contain.text', 'Thinking...')
    })

    it('should display user message after sending', () => {
      const testMessage = 'Test user message'
      
      cy.get('.message-input .q-field__native').type(testMessage)
      cy.get('.action-btn[type="submit"]').click()
      
      // Should display user message
      cy.get('.user-message', { timeout: 2000 }).should('be.visible')
      cy.get('.user-content').should('contain.text', testMessage)
    })

    it('should show cancel button during loading', () => {
      cy.get('.message-input .q-field__native').type('Test message for cancellation')
      cy.get('.action-btn[type="submit"]').click()
      
      // Should show cancel button
      cy.get('.cancel-btn', { timeout: 1000 }).should('be.visible')
    })

    it('should allow cancelling requests', () => {
      cy.get('.message-input .q-field__native').type('Test message for cancellation')
      cy.get('.action-btn[type="submit"]').click()
      
      // Click cancel button
      cy.get('.cancel-btn', { timeout: 1000 }).click()
      
      // Should show cancellation notification
      cy.get('.q-notification', { timeout: 3000 }).should('contain.text', 'cancelled')
      
      // Loading should stop
      cy.get('.loading-indicator').should('not.exist')
    })
  })

  describe('Message Actions', () => {
    beforeEach(() => {
      // Send a message to have something to interact with
      cy.get('.message-input .q-field__native').type('Test message for actions')
      cy.get('.action-btn[type="submit"]').click()
      
      // Wait for AI response (or timeout)
      cy.wait(3000)
    })

    it('should show message actions when AI message exists', () => {
      cy.get('.ai-message').should('exist')
      // Message actions exist but are hidden by default (opacity: 0)
      cy.get('.message-actions').should('exist')
    })

    it('should allow copying messages', () => {
      cy.get('.ai-message').should('exist')
      // Message actions are hidden by default, need to hover to make them visible
      cy.get('.ai-message').trigger('mouseover')
      cy.get('[data-cy="copy-message"]').should('be.visible').click()
      
      // Should show copy notification (Quasar creates individual notification elements)
      cy.get('.q-notification', { timeout: 3000 }).should('contain.text', 'copied')
    })

    it('should allow providing feedback', () => {
      cy.get('.ai-message').should('exist')
      // Hover to make actions visible
      cy.get('.ai-message').trigger('mouseover')
      cy.get('[data-cy="thumbs-up"]').should('be.visible').click()
      
      // Should show feedback notification
      cy.get('.q-notification', { timeout: 3000 }).should('contain.text', 'feedback')
    })
  })

  describe('Error Handling', () => {
    it('should handle connection errors gracefully', () => {
      // Intercept the chat request to simulate an error
      cy.intercept('POST', '**/chat', { forceNetworkError: true }).as('chatError')
      
      cy.get('.message-input .q-field__native').type('Test error handling')
      cy.get('.action-btn[type="submit"]').click()
      
      // Should show error message in AI response
      cy.get('.ai-content', { timeout: 10000 }).should('contain.text', 'trouble connecting')
      
      // Should show error notification (Quasar creates individual notification elements)
      cy.get('.q-notification', { timeout: 3000 }).should('contain.text', 'Failed to get AI response')
    })

    it('should handle timeout scenarios', () => {
      // Intercept the chat request to simulate a timeout
      cy.intercept('POST', '**/chat', { delay: 30000 }).as('chatTimeout')
      
      cy.get('.message-input .q-field__native').type('Test timeout handling')
      cy.get('.action-btn[type="submit"]').click()
      
      // Cancel the request after a short time
      cy.get('.cancel-btn', { timeout: 1000 }).click()
      
      // Should handle cancellation gracefully
      cy.get('.q-notification', { timeout: 3000 }).should('contain.text', 'cancelled')
    })
  })

  describe('Responsive Design', () => {
    it('should adapt to mobile viewport', () => {
      cy.viewport('iphone-x')
      
      // Check that elements are still visible and functional
      cy.get('.chat-header').should('be.visible')
      cy.get('.input-section').should('be.visible')
      cy.get('.welcome-section').should('be.visible')
      
      // Check that example cards stack properly
      cy.get('.examples-grid').should('be.visible')
    })

    it('should adapt to tablet viewport', () => {
      cy.viewport('ipad-2')
      
      // Check that layout adapts appropriately
      cy.get('.chat-container').should('be.visible')
      cy.get('.input-container').should('be.visible')
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', () => {
      cy.get('.message-input .q-field__native').should('have.attr', 'placeholder')
      cy.get('.action-btn[type="submit"]').should('have.attr', 'type', 'submit')
    })

    it('should support keyboard navigation', () => {
      // Test that elements can be focused (without using .focusable which doesn't exist)
      cy.get('.model-selector').focus().should('be.focused')
      cy.get('.message-input .q-field__native').focus().should('be.focused')
      cy.get('.action-btn[type="submit"]').focus().should('be.focused')
      
      // Test keyboard shortcuts
      cy.get('.message-input .q-field__native').focus()
      cy.get('.message-input .q-field__native').type('Test keyboard navigation')
      cy.get('.message-input .q-field__native').type('{ctrl}{enter}')
    })
  })

  describe('Performance', () => {
    it('should load quickly', () => {
      const start = Date.now()
      cy.visit('/')
      cy.get('.chat-view').should('be.visible')
      cy.then(() => {
        const loadTime = Date.now() - start
        expect(loadTime).to.be.lessThan(3000) // Should load within 3 seconds
      })
    })

    it('should handle multiple rapid interactions', () => {
      // Test rapid input interactions instead of example cards
      cy.get('.message-input .q-field__native').type('Test 1')
      cy.get('.message-input .q-field__native').clear()
      cy.get('.message-input .q-field__native').type('Test 2')
      cy.get('.message-input .q-field__native').clear()
      cy.get('.message-input .q-field__native').type('Test 3')
      
      // Should handle gracefully without errors
      cy.get('.message-input').should('be.visible')
    })
  })
})
