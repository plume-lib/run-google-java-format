;; Emacs Lisp code to automatically format your code when you save it.

(defun update-java-mode-hook-for-gjf ()
  (add-hook 'after-save-hook 'run-google-java-format nil 'local))
(add-hook 'java-mode-hook 'update-java-mode-hook-for-gjf)

(defun run-google-java-format ()
  "Run external program run-google-java-format.py on the file,
if it matches a hard-coded list of directories."
  (interactive)
  (let ((cmd
         (cond
          ((or (and (string-match-p "/\\(randoop\\)" (buffer-file-name))
                    (not (string-match-p "CloneVisitor\\.java$" (buffer-file-name))))
               (and (string-match-p "/daikon" (buffer-file-name))
                    (not (string-match-p "\\.jpp$" (buffer-file-name))))
               (and (string-match-p "/toradocu" (buffer-file-name))
                    (not (string-match-p "/src/test/resources/" (buffer-file-name))))
               (and (string-match-p "/plume-lib" (buffer-file-name))
                    (not (string-match-p "WeakHasherMap.java$\\|WeakIdentityHashMap.java$"
                                         (buffer-file-name))))
               (string-match-p "/org/plumelib/" (buffer-file-name)))
           ;; normal formatting
           "run-google-java-format.py ")
          ((and (string-match-p "/checker-framework" (buffer-file-name))
                (not (string-match-p "/checker-framework-inference" (buffer-file-name)))
                (not (string-match-p "/checker/jdk/" (buffer-file-name)))
                (not (string-match-p "\\.astub$" (buffer-file-name)))
                )
           ;; non-standard cammand-line arguments
           "run-google-java-format.py -a ")
          (t
           ;; for all other projects, don't automatically reformat
           nil))))
    (if cmd
        (progn
          ;; I would like to avoid the "(Shell command succeeded with no output)"
          ;; message.
          (shell-command (concat cmd (buffer-file-name)) "*run-google-java-format*")
          ;; If you use bdiff, use this version instead
          ;; (bdiff-revert-buffer-maybe)
          (revert-buffer nil t)))))
