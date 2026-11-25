module

public import Mathlib.Data.Finset.Max

/-!
# Lean economics pilot

* Each agent chooses from a finite private menu using a score `Nat → Nat`.
* Requests are natural numbers.
* Two simultaneous requests are checked against one stock.
-/

@[expose] public section

namespace LeanEconPilot

/-! ## Choice from a finite menu -/

/-- Returns the highest-scoring menu members, including all ties. -/
def bestRequests (menu : Finset Nat) (score : Nat → Nat) : Finset Nat :=
  menu.filter (fun request => ∀ other ∈ menu, score other ≤ score request)

theorem mem_bestRequests {menu : Finset Nat} {score : Nat → Nat} {request : Nat} :
    request ∈ bestRequests menu score ↔
      request ∈ menu ∧ ∀ other ∈ menu, score other ≤ score request := by
  unfold bestRequests
  exact Finset.mem_filter

/-- Every nonempty finite menu has at least one score-maximal member. -/
theorem bestRequests_nonempty {menu : Finset Nat} (score : Nat → Nat)
    (h : menu.Nonempty) : (bestRequests menu score).Nonempty := by
  obtain ⟨request, h_mem, h_max⟩ := Finset.exists_max_image menu score h
  exact ⟨request, mem_bestRequests.mpr ⟨h_mem, h_max⟩⟩

/-- A menu member tied with a maximizer is also a maximizer. -/
theorem bestRequests_keeps_ties {menu : Finset Nat} {score : Nat → Nat}
    {best other : Nat} (h_best : best ∈ bestRequests menu score)
    (h_other : other ∈ menu) (h_tie : score other = score best) :
    other ∈ bestRequests menu score := by
  obtain ⟨_, h_max⟩ := mem_bestRequests.mp h_best
  refine mem_bestRequests.mpr ⟨h_other, fun x hx => ?_⟩
  rw [h_tie]
  exact h_max x hx

/-! ## Joint allocation from a shared stock -/

/-- Constraints on the pair of grants for two simultaneous requests against one stock. -/
structure Clears (stock : Nat) (requests grants : Nat × Nat) : Prop where
  first_capped : grants.1 ≤ requests.1
  second_capped : grants.2 ≤ requests.2
  within_stock : grants.1 + grants.2 ≤ stock
  spare_fills_all : grants.1 + grants.2 < stock →
    grants.1 = requests.1 ∧ grants.2 = requests.2

/-- Serve the first request from the opening stock. Serve the second from what remains. -/
def firstPriority (stock : Nat) (requests : Nat × Nat) : Nat × Nat :=
  (min requests.1 stock, min requests.2 (stock - min requests.1 stock))

theorem firstPriority_clears (stock : Nat) (requests : Nat × Nat) :
    Clears stock requests (firstPriority stock requests) := by
  refine ⟨?_, ?_, ?_, ?_⟩ <;> simp only [firstPriority] <;> omega

/-- Every admissible clearing allocates exactly `min stock (total requests)`. -/
theorem Clears.total_eq_min {stock : Nat} {requests grants : Nat × Nat}
    (h : Clears stock requests grants) :
    grants.1 + grants.2 = min stock (requests.1 + requests.2) := by
  have h1 := h.first_capped
  have h2 := h.second_capped
  have h3 := h.within_stock
  by_cases h_spare : grants.1 + grants.2 < stock
  · obtain ⟨e1, e2⟩ := h.spare_fills_all h_spare
    omega
  · omega

/-- Stock left unallocated after the grants. -/
def unallocated (stock : Nat) (grants : Nat × Nat) : Nat :=
  stock - (grants.1 + grants.2)

/-- Granted plus unallocated stock equals the opening stock exactly. -/
theorem Clears.conserves {stock : Nat} {requests grants : Nat × Nat}
    (h : Clears stock requests grants) :
    grants.1 + grants.2 + unallocated stock grants = stock := by
  have h3 := h.within_stock
  unfold unallocated
  omega

/-! ## Individual feasibility and joint scarcity -/

/-- With menu `{0, 1}` and score `id`, each agent's only maximal request is 1.
Stock 1 can fill either request in isolation. Joint clearing leaves one request unfilled. -/
theorem selected_requests_not_jointly_fillable :
    bestRequests {0, 1} id = {1} ∧
    Clears 1 (1, 0) (1, 0) ∧
    Clears 1 (0, 1) (0, 1) ∧
    ∀ grants, Clears 1 (1, 1) grants → ¬ (grants.1 = 1 ∧ grants.2 = 1) := by
  refine ⟨by decide, ⟨by decide, by decide, by decide, by decide⟩,
    ⟨by decide, by decide, by decide, by decide⟩, ?_⟩
  intro grants h ⟨e1, e2⟩
  have h3 := h.within_stock
  omega

/-- The same inputs allow either singleton grant, `(1, 0)` or `(0, 1)`.
`firstPriority` returns `(1, 0)`. -/
theorem clears_leaves_rationing_open :
    Clears 1 (1, 1) (1, 0) ∧ Clears 1 (1, 1) (0, 1) ∧
    firstPriority 1 (1, 1) = (1, 0) :=
  ⟨⟨by decide, by decide, by decide, by decide⟩,
    ⟨by decide, by decide, by decide, by decide⟩, by decide⟩

end LeanEconPilot

/-! ## Axiom audit -/

/-- info: 'LeanEconPilot.mem_bestRequests' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms LeanEconPilot.mem_bestRequests

/-- info: 'LeanEconPilot.bestRequests_nonempty' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms LeanEconPilot.bestRequests_nonempty

/-- info: 'LeanEconPilot.bestRequests_keeps_ties' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms LeanEconPilot.bestRequests_keeps_ties

/-- info: 'LeanEconPilot.firstPriority_clears' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms LeanEconPilot.firstPriority_clears

/-- info: 'LeanEconPilot.Clears.total_eq_min' depends on axioms: [propext, Quot.sound] -/
#guard_msgs in
#print axioms LeanEconPilot.Clears.total_eq_min

/-- info: 'LeanEconPilot.Clears.conserves' depends on axioms: [propext, Quot.sound] -/
#guard_msgs in
#print axioms LeanEconPilot.Clears.conserves

/-- info: 'LeanEconPilot.selected_requests_not_jointly_fillable' depends on axioms: [propext, Classical.choice, Quot.sound] -/
#guard_msgs in
#print axioms LeanEconPilot.selected_requests_not_jointly_fillable

/-- info: 'LeanEconPilot.clears_leaves_rationing_open' does not depend on any axioms -/
#guard_msgs in
#print axioms LeanEconPilot.clears_leaves_rationing_open

end
