theory DeepSeekTest
  imports Main
begin

lemma substitution_test:
  fixes a b :: nat
  assumes "a = b"
  shows "a + a = b + b"
  using assms by simp

end
