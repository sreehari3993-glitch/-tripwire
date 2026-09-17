import React, { createContext, useContext, useState } from 'react'
import DemoModal from '../components/DemoModal'
import SystemComparisonModal from '../components/SystemComparisonModal'
import PrivacyEthicsModal from '../components/PrivacyEthicsModal'
import ModelValidationModal from '../components/ModelValidationModal'

const ModalContext = createContext(null)

export function ModalProvider({ children }) {
  const [isDemoOpen, setIsDemoOpen] = useState(false)
  const [isComparisonOpen, setIsComparisonOpen] = useState(false)
  const [isPrivacyOpen, setIsPrivacyOpen] = useState(false)
  const [isValidationOpen, setIsValidationOpen] = useState(false)

  return (
    <ModalContext.Provider
      value={{
        isDemoOpen,
        openDemo: () => setIsDemoOpen(true),
        closeDemo: () => setIsDemoOpen(false),
        isComparisonOpen,
        openComparison: () => setIsComparisonOpen(true),
        closeComparison: () => setIsComparisonOpen(false),
        isPrivacyOpen,
        openPrivacy: () => setIsPrivacyOpen(true),
        closePrivacy: () => setIsPrivacyOpen(false),
        isValidationOpen,
        openValidation: () => setIsValidationOpen(true),
        closeValidation: () => setIsValidationOpen(false),
      }}
    >
      {children}
      <DemoModal isOpen={isDemoOpen} onClose={() => setIsDemoOpen(false)} />
      <SystemComparisonModal isOpen={isComparisonOpen} onClose={() => setIsComparisonOpen(false)} />
      <PrivacyEthicsModal isOpen={isPrivacyOpen} onClose={() => setIsPrivacyOpen(false)} />
      <ModelValidationModal isOpen={isValidationOpen} onClose={() => setIsValidationOpen(false)} />
    </ModalContext.Provider>
  )
}


export const useModals = () => useContext(ModalContext)
